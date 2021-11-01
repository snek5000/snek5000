import pymech as pm
import pytest

from snek5000.output import _make_path_session
from snek5000.util.restart import SnekRestartError, get_status, load_for_restart


def test_too_early(sim_data):
    assert get_status(sim_data).code == 425

    with pytest.raises(SnekRestartError, match="425: Too Early"):
        load_for_restart(sim_data)


def test_locked(sim_data):
    locks_dir = sim_data / ".snakemake" / "locks"
    locks_dir.mkdir(parents=True)
    (locks_dir / "lock").touch()

    assert get_status(sim_data).code == 423


def test_ok(sim_data):
    (sim_data / ".snakemake").mkdir()
    session = _make_path_session(sim_data, 0)
    [file.unlink() for file in session.glob("phill*0.f?????")]

    assert get_status(sim_data).code == 200


def test_reset_content(sim_data):
    (sim_data / ".snakemake").mkdir()

    assert get_status(sim_data).code == 205


def test_not_found(sim_data):
    (sim_data / ".snakemake").mkdir()
    (sim_data / "nek5000").unlink()

    assert get_status(sim_data).code == 404


def test_partial_content(sim_data):
    (sim_data / ".snakemake").mkdir()
    session = _make_path_session(sim_data, 0)
    [restart.unlink() for restart in session.glob("rs6*")]

    assert get_status(sim_data).code == 206


def test_restart_error(tmpdir):
    with pytest.raises(SnekRestartError, match="425: Too Early"):
        load_for_restart(tmpdir)


@pytest.mark.slow
def test_restart(sim_executed):
    # In real workflows, to pre load data in preperation for restart, use:
    # >>> sim_executed = snek5000.load()
    fld_file = sim_executed.output.get_field_file()

    fld = pm.readnek(fld_file)
    params, Simul = load_for_restart(
        sim_executed.path_run, use_start_from=fld_file.name
    )

    assert params.output.HAS_TO_SAVE
    assert not params.NEW_DIR_RESULTS

    t_end = params.nek.general.end_time = fld.time + 10 * abs(
        params.nek.general.dt
    )  # In phill for some reason dt is negative

    sim = Simul(params)
    sim.make.exec(["run_fg"])

    fld = pm.readnek(sim.output.get_field_file())
    assert fld.time == t_end
