"""Snakemake interface
======================

"""
import os
from pathlib import Path
from typing import Iterable
from warnings import warn

from snakemake import snakemake
from snakemake.executors import change_working_directory as change_dir


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

    def exec(
        self,
        *rules,
        dryrun=False,
        keep_incomplete=True,
        env_vars_configfile=None,
        **kwargs,
    ):
        """Execute snakemake rules in sequence.

        Parameters
        ----------
        rules: iterable of str, positional-only
            Snakemake rules to be executed. Default rule is `"run"`
        dryrun: bool
            Dry run snakemake rules without executing
        keep_incomplete: bool
            Keep incomplete output files of failed jobs
        env_vars_configfile: dict (None)
            Environment variables given to Snake via a custom config file.

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

        if env_vars_configfile:
            path_configfile0 = self.sim.output.get_configfile()
            import yaml

            with open(path_configfile0) as file:
                config = yaml.safe_load(file)
            config.update(env_vars_configfile)

            path_custom_configfile = Path(self.sim.path_run) / "custom_configfile.yml"
            with open(path_custom_configfile, "w") as file:
                yaml.dump(config, file)

            os.environ["SNEK_CONFIGFILE"] = str(path_custom_configfile)

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
