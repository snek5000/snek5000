"""Snakemake interface
======================

"""
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

    def __init__(self, sim):
        self.sim = sim
        self.path_run = sim.output.path_run
        try:
            self.file = next(f for f in sim.output.get_paths() if f.name == "Snakefile")
        except AttributeError:
            raise AttributeError("Unable to get path of Snakefile via Output class")
        except StopIteration:
            raise FileNotFoundError(f"No Snakefile in {self.path_run}")

        self.log_handler = []

    def list(self):
        """List rules.

        Equivalent to::

          snakemake --list-target-rules

        """
        with change_dir(self.path_run):
            return snakemake(self.file, listrules=True, log_handler=self.log_handler)

    def exec(self, *rules, dryrun=False, keep_incomplete=True, **kwargs):
        """Execute snakemake rules in sequence.

        Parameters
        ----------
        rules: iterable of str, positional-only
            Snakemake rules to be executed. Default rule is `"run"`
        dryrun: bool
            Dry run snakemake rules without executing
        keep_incomplete: bool
            Keep incomplete output files of failed jobs

        Notes
        -----

        For more on available keyword arguments refer to `Snakemake API documentation`_.

        .. _Snakemake API documentation: https://snakemake.readthedocs.io/en/stable/api_reference/snakemake.html

        Returns
        -------
        bool
            ``True`` if workflow execution was successful.

        Examples
        --------

        >>> sim.make.exec('mesh', 'SESSION.NAME')
        >>> sim.make.exec('compile')
        >>> sim.make.exec('run', resources={'nproc': 4})

        It is also possible to do the same directly from command line
        by changing to the simulation directory and executing::

          snakemake -j1 compile
          snakemake -j1 --resources nproc=2 run

        The flag ``-j`` is short for ``--jobs`` and sets the number of
        threads available for snakemake rules to execute.

        The list of the available target rules can be obtained with:

        >>> sim.make.list()

        or from command line with::

          snakemake --list-target-rules

        .. seealso:: Useful Snakemake `command line arguments`_

        .. _command line arguments: https://snakemake.readthedocs.io/en/stable/executing/cli.html#useful-command-line-arguments

        """
        # Default rule
        if not rules:
            rules = ("run",)

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
                **kwargs,
            )


class _Nek5000Make(Make):
    """Snakemake interface to build Nek5000 tools and other dependencies."""

    def __init__(self):
        self.path_run = Path(snek5000.get_nek_source_root())
        self.file = snek5000.get_asset("nek5000.smk")
        self.lock = FileLock(self.path_run / "nek5000_make_config.yml.lock")
        self.config_cache = self.path_run / "nek5000_make_config.yml"
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
                return self.exec(*self.targets, config=config)
            else:
                return True
