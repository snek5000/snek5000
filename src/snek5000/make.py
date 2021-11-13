"""Snakemake interface
======================

"""
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
        """List rules."""
        with change_dir(self.path_run):
            return snakemake(self.file, listrules=True, log_handler=self.log_handler)

    def exec(
        self, rule="run", /, *extra_rules, dryrun=False, keep_incomplete=True, **kwargs
    ):
        """Execute snakemake rules in sequence.

        Parameters
        ---------------------
        rule: str, positional-only
            Snakemake rules to be executed
        *extra_rules: iterable of str, positional-only
            Extra snakemake rules to be executed
        dryrun: bool
            Dry run snakemake rules without executing
        keep_incomplete: bool
            Keep incomplete output files of failed jobs


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

            snakemake -j compile
            snakemake -j1 --resources nproc=2 run

        The flag ``-j`` is short for ``--jobs`` and sets the number of
        threads available for snakemake rules to execute.

        .. seealso:: Useful Snakemake `command line arguments`_

        .. _command line arguments: https://snakemake.readthedocs.io/en/stable/executing/cli.html#useful-command-line-arguments

        """
        if not isinstance(rule, str) and isinstance(rule, Iterable) and not extra_rules:
            warn(
                (
                    f"Rules {rule} should be passed as positional arguments, "
                    "i.e. a string or comma separated strings; and not as a "
                    f"{type(rule)}. Changed in snek5000 0.8.0b0."
                ),
                DeprecationWarning,
            )
            rules = rule
        else:
            rules = (rule, *extra_rules)

        with change_dir(self.path_run):
            return snakemake(
                self.file,
                targets=rules,
                dryrun=dryrun,
                keep_incomplete=keep_incomplete,
                log_handler=self.log_handler,
                **kwargs,
            )
