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
            raise AttributeError("Unable to get path of Snakefile via Output class.")

        self.log_handler = []

    def list(self):
        """List rules."""
        with change_dir(self.path_run):
            return snakemake(self.file, listrules=True, log_handler=self.log_handler)

    def exec(self, rules=("run",), dryrun=False, **kwargs):
        """Execute snakemake rules in sequence.

        :returns: True if workflow execution was successful.

        """
        with change_dir(self.path_run):
            return snakemake(
                self.file,
                targets=rules,
                dryrun=dryrun,
                log_handler=self.log_handler,
                **kwargs
            )
