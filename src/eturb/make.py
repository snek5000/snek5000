from snakemake import snakemake, Batch
from .util import change_dir


class Make:
    def __init__(self, sim):
        self.sim = sim
        try:
            self.file = next(f for f in sim.output.get_paths() if f.name == "Snakefile")
        except AttributeError:
            raise AttributeError("Unable to get path of Snakefile via Output class.")

    @staticmethod
    def _generate_batch(rules):
        """Generate a batch of snakemake rules to execute

        :param rules: Iterable of strings representing snakemake rules.
        """
        rules = tuple(rules)
        nb_batches = len(rules)
        return (
            Batch(rulename, idx+1, nb_batches) for idx, rulename in enumerate(rules)
        )

    def exec(self, rules):
        """Execute snakemake rules in sequence."""
        batches = self._generate_batch(rules)
        path_run = self.sim.path_run
        with change_dir(path_run):
            for batch in batches:
                snakemake(self.file, batch)
