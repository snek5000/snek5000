"""Snakemake interface
======================

"""
from snakemake import snakemake
from .util import change_dir


class Make:
    """Snakemake interface for the solvers.

    :param sim: A simulation instance

    """
    def __init__(self, sim):
        self.sim = sim
        self.path_run = sim.output.path_run
        try:
            self.file = next(
                f for f in sim.output.get_paths() if f.name == "Snakefile"
            )
        except AttributeError:
            raise AttributeError(
                "Unable to get path of Snakefile via Output class."
            )

    def list(self):
        """List rules."""
        with change_dir(self.path_run):
            snakemake(self.file, workdir=self.path_run, listrules=True)

    def exec(self, rules=('run',), dryrun=False):
        """Execute snakemake rules in sequence."""
        with change_dir(self.path_run):
            snakemake(self.file, targets=rules, dryrun=dryrun)
