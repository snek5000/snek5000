from snek5000.util.restart import get_status, prepare_for_restart


def test_425(sim_data, caplog):
    assert get_status(sim_data).code == 425

    prepare_for_restart(sim_data)
    assert "425: Too Early" in caplog.text, "Expected status 425"


def test_423(sim_data):
    locks_dir = sim_data / ".snakemake" / "locks"
    locks_dir.mkdir(parents=True)
    (locks_dir / "lock").touch()

    assert get_status(sim_data).code == 423


def test_200(sim_data):
    (sim_data / ".snakemake").mkdir()

    assert get_status(sim_data).code == 200


def test_404(sim_data):
    (sim_data / ".snakemake").mkdir()
    (sim_data / "nek5000").unlink()

    assert get_status(sim_data).code == 404


def test_417(sim_data):
    (sim_data / ".snakemake").mkdir()
    [restart.unlink() for restart in sim_data.glob("rs6*")]

    assert get_status(sim_data).code == 417
