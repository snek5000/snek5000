import os

from snek5000.util.archive import archive, clean_simul, tar_name


def test_name(sim_data):
    root_name = "phill"
    pattern = str(sim_data / "*")
    ark_tar_gz = tar_name(root_name, pattern, compress_format=".gz")
    assert ark_tar_gz


def test_compress(sim_data):
    contents = sorted(sim_data.iterdir())
    half = len(contents) // 2

    archive(sim_data / "ark.tar", contents[:half], remove=True)
    archive(sim_data / "ark.tar", contents[half:])
    archive(sim_data / "ark.tar.gz", readonly=True)

    os.chdir(str(sim_data))
    clean_simul("phill", "ark.tar.gz")
