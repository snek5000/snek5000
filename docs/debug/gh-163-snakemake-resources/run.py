from functools import partial

from snakemake import snakemake

make = partial(
    snakemake,
    snakefile="Snakefile",
    targets=("earth", "space"),
    printshellcmds=True,
)


def test_resources(capsys):
    # assert make(resources={"alien": 42})
    assert make(overwrite_resources={"space": {"alien": 42}})
    out, err = capsys.readouterr()
    assert "hello alien number 42" in err


if __name__ == "__main__":
    make()
    make(resources={"alien": 42})
    make(overwrite_resources={"space": {"alien": 42}})
