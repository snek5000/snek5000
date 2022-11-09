from functools import partial

from snakemake import snakemake

make = partial(snakemake, snakefile="Snakefile", targets=("earth", "space"))
make()
make(resources={"alien": 42})
make(overwrite_resources={"space": {"alien": 42}})
