"""Snakemake interface
======================

"""
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable
from warnings import warn

import yaml
from filelock import FileLock
from snakemake import snakemake
from snakemake.executors import change_working_directory as change_dir

import snek5000


def unlock(path_dir):
    """Unlock a directory locked using Snakemake."""
    with change_dir(path_dir):
        snakemake("Snakefile", unlock=True)


class Make:
    """Snakemake interface for the solvers.

    :param sim: A simulation instance

    """

    def __init__(self, sim=None, path_run=None, snakefile=None):
        if (sim is None and path_run is None) or (
            sim is not None and path_run is not None
        ):
            raise ValueError("Either sim of path_run has to be given.")

        if snakefile:
            snakefile = Path(snakefile)

        if path_run is None:
            self.path_run = sim.output.path_run
            try:
                self.file = snakefile or next(
                    f for f in sim.output.get_paths() if f.name == "Snakefile"
                )
            except AttributeError:
                raise AttributeError("Unable to get path of Snakefile via Output class")
            except StopIteration:
                raise FileNotFoundError(f"No Snakefile in {self.path_run}")
        else:
            if not path_run.exists():
                raise FileNotFoundError(f"{path_run} does not exist.")
            self.path_run = Path(path_run)
            self.file = snakefile or self.path_run / "Snakefile"
            if not self.file.exists():
                raise FileNotFoundError(f"No Snakefile in {path_run}")

        self.log_handler = []

    def list(self, **kwargs):
        """List rules.

        Equivalent to::

          snakemake --list-target-rules

        """
        with change_dir(self.path_run):
            return snakemake(
                self.file, listrules=True, log_handler=self.log_handler, **kwargs
            )

    def exec(
        self,
        *rules,
        set_resources=None,
        dryrun=False,
        keep_incomplete=True,
        nproc=None,
        **kwargs,
    ):
        """Execute snakemake rules in sequence.

        Parameters
        ----------
        rules: iterable of str, positional-only
            Snakemake rules to be executed. Default rule is `"run"`
        set_resources: dict[str, int]
            Resources to override (see example below).
        dryrun: bool
            Dry run snakemake rules without executing
        keep_incomplete: bool
            Keep incomplete output files of failed jobs
        nproc: Optional[int]
            Number of MPI processes

        Notes
        -----

        For more on available keyword arguments refer to `Snakemake API documentation`_.

        .. _Snakemake API documentation: https://snakemake-api.readthedocs.io/en/stable/api_reference/snakemake.html

        Returns
        -------
        bool
            ``True`` if workflow execution was successful.

        Examples
        --------

        >>> sim.make.exec('mesh', 'SESSION.NAME')
        >>> sim.make.exec('compile')
        >>> sim.make.exec('run', set_resources={'nproc': 4})
        >>> sim.make.exec('run_fg', nproc=2)

        It is also possible to do the same directly from command line
        by changing to the simulation directory and executing::

          snek-make -h
          snek-make compile
          snakemake -j1 compile
          snakemake -j1 --set-resources='run:nproc=4' run

        The flag ``-j`` is short for ``--jobs`` and sets the number of
        threads available for snakemake rules to execute.

        The list of the available target rules can be obtained with:

        >>> sim.make.list()

        or from command line with::

          snek-make -l
          snakemake --list-target-rules

        .. seealso:: Useful Snakemake `command line arguments`_

        .. _command line arguments: https://snakemake.readthedocs.io/en/stable/executing/cli.html#useful-command-line-arguments

        """
        # Default rule
        if not rules:
            rules = ("run",)

        if "resources" in kwargs and not set_resources:
            warn(
                (
                    "Setting `resources` does not have the intended effect. "
                    "Converting `resources` to `set_resources`. "
                    "Use `set_resources` instead in the future."
                ),
                DeprecationWarning,
            )
            set_resources = kwargs.pop("resources")

        if nproc is not None:
            if set_resources is None:
                set_resources = {"nproc": nproc}
            else:
                set_resources["nproc"] = nproc

        if set_resources:
            overwrite_resources = {rule: set_resources for rule in rules}
        else:
            overwrite_resources = None

        # Check if rules were passed as a list / tuple (old API)
        first_rule = rules[0]
        if (
            not isinstance(first_rule, str)
            and isinstance(first_rule, Iterable)
            and len(rules) == 1
        ):
            warn(
                (
                    f"Rules {first_rule} should be passed as positional arguments, "
                    "i.e. a string or comma separated strings; and not as a "
                    f"{type(first_rule)}. Changed in snek5000 0.8.0b0."
                ),
                DeprecationWarning,
            )
            rules = first_rule

        with change_dir(self.path_run):
            return snakemake(
                self.file,
                targets=rules,
                dryrun=dryrun,
                keep_incomplete=keep_incomplete,
                log_handler=self.log_handler,
                overwrite_resources=overwrite_resources,
                **kwargs,
            )


class _Nek5000Make(Make):
    """Snakemake interface to build Nek5000 tools and other dependencies.
    This class would prevent unnecessary rebuild of Nek5000 if there is no
    change in the compiler configuration.

    """

    def __init__(self):
        #: ``NEK_SOURCE_ROOT`` is the working directory
        self.path_run = Path(snek5000.get_nek_source_root())

        #: The ``nek5000.smk`` Snakemake file from :mod:`snek5000.resources` is used here
        self.file = snek5000.get_snek_resource("nek5000.smk")

        #: A file lock ``nek5000_make_config.yml.lock`` used to prevent race conditions
        self.lock = FileLock(self.path_run / "nek5000_make_config.yml.lock")

        #: A YAML file ``nek5000_make_config.yml`` to record compiler configuration
        self.config_cache = self.path_run / "nek5000_make_config.yml"

        #: List of files to build
        self.targets = [
            "bin/genbox",
            "bin/genmap",
            "3rd_party/gslib/lib/libgs.a",
            "3rd_party/blasLapack/libblasLapack.a",
        ]

        # TODO: replace with Snek5000 log handler?
        self.log_handler = []

    def has_to_build(self, compiler_config):
        compiler_config_str = yaml.safe_dump(compiler_config)
        compiler_config_cache = (
            self.config_cache.read_text() if self.config_cache.exists() else ""
        )

        if (
            # One or more of the targets do not exist
            any(not (self.path_run / target).exists() for target in self.targets)
            or compiler_config_str != compiler_config_cache
            # New compiler configuration
        ):
            # Save new configuration first
            self.config_cache.write_text(compiler_config_str)

            return True
        else:
            return False

    def build(self, config):
        """Build Nek5000 tools and third party libraries essential for a
        simulation.

        Parameters
        ----------
        config: dict
            Snakemake configuration

        Returns
        -------
        bool
            ``True`` if workflow execution was successful.

        """

        compiler_config = {
            key: config[key]
            for key in (
                "CC",
                "FC",
                "MPICC",
                "MPIFC",
                "CFLAGS",
                "FFLAGS",
            )
        }

        with self.lock:
            # Only one process can inspect at a time. No timeout
            if self.has_to_build(compiler_config):
                return self.exec(*self.targets, config=config, force_incomplete=True)
            else:
                return True


def snek_make():
    """Used for the command snek-make"""
    parser = argparse.ArgumentParser(
        prog="snek-make",
        description="Execute Snakemake rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "rule",
        nargs="?",
        default=None,
        help="Snakemake rule to be executed.",
    )
    parser.add_argument(
        "-l",
        "--list-rules",
        action="store_true",
        help="List rules and exit.",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Dry run snakemake rules without executing.",
    )
    parser.add_argument(
        "-np",
        "--nproc",
        type=int,
        default=None,
        help="Number of MPI processes.",
    )
    parser.add_argument(
        "--clean-after-fail",
        action="store_true",
        help="Clean incomplete output files of failed jobs.",
    )

    args = parser.parse_args()

    make = Make(path_run=Path.cwd())

    if args.rule is None:
        print("You need to specify a rule to be executed")

    if args.list_rules or args.rule is None:
        make.list()
        sys.exit(0)

    make.exec(
        args.rule,
        dryrun=args.dry_run,
        keep_incomplete=not args.clean_after_fail,
        nproc=args.nproc,
    )


def snek_make_nek():
    """Used for the command snek-make-nek"""
    parser = argparse.ArgumentParser(
        prog="snek-make-nek",
        description="Execute Snakemake rules to build Nek5000 tools and libraries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "rule",
        nargs="?",
        default=None,
        help="Snakemake rule to be executed.",
    )
    parser.add_argument(
        "-l",
        "--list-rules",
        action="store_true",
        help="List rules and exit.",
    )
    parser.add_argument(
        "-c",
        "--clean-git",
        action="store_true",
        help="Apply git-clean on Nek5000 repository before building.",
    )

    args = parser.parse_args()

    # make = Make(path_run=Path(snek5000.get_nek_source_root()), snakefile=snek5000.get_snek_resource("nek5000.smk"))
    #
    make = _Nek5000Make()

    from snek5000.output.base import Output

    with Output.find_configfile().open() as fp:
        config = yaml.safe_load(fp)

    Output.update_snakemake_config(config, "snek-make-nek", env_sensitive=True)

    if args.list_rules:
        make.list(config=config)
        sys.exit(0)

    if args.clean_git:
        with change_dir(snek5000.get_nek_source_root()):
            subprocess.run(["git", "clean", "-xdf"])

    if args.rule is None:
        make.build(config)
    else:
        make.exec(args.rule, nproc=4, config=config)
