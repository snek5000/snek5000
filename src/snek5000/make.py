"""Snakemake interface
======================

"""
from snakemake import snakemake
from snakemake.executors import change_working_directory as change_dir


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

    def exec(self, rules=("run",), dryrun=False, **kwargs):
        """Execute snakemake rules in sequence.

        :param iterable rules: Snakemake rules to be executed
        :param bool dryrun: Dry run snakemake without executing

        For more on available keyword arguments refer to `Snakemake API documentation`_.

        :returns: True if workflow execution was successful.

        .. _Snakemake API documentation: https://snakemake.readthedocs.io/en/stable/api_reference/snakemake.html

        Examples
        --------

        >>> sim.make.exec(['compile'])
        >>> sim.make.exec(['run'], resources={'nproc': 4})

        It is also possible to do the same directly from command line
        by changing to the simulation directory and executing::

            snakemake -j compile
            snakemake -j1 --resources nproc=2 run

        The flag ``-j`` is short for ``--jobs`` and sets the number of
        threads available for snakemake rules to execute.

        .. seealso:: Useful Snakemake `command line arguments`_

        .. _command line arguments: https://snakemake.readthedocs.io/en/stable/executing/cli.html#useful-command-line-arguments

        """
        with change_dir(self.path_run):
            return snakemake(
                self.file,
                targets=rules,
                dryrun=dryrun,
                log_handler=self.log_handler,
                **kwargs,
            )
