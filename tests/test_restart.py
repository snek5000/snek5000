import pymech as pm
import pytest

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
    [file.unlink() for file in sim_data.glob("phill*0.f?????")]

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
    [restart.unlink() for restart in sim_data.glob("rs6*")]

    assert get_status(sim_data).code == 206


def test_restart_error(tmpdir):
    with pytest.raises(SnekRestartError, match="425: Too Early"):
        load_for_restart(tmpdir)


@pytest.mark.slow
def test_restart(sim_executed):
    params, Simul = load_for_restart(sim_executed.path_run)

    # TODO: overwrite params xml and par file
    sim = Simul(params)
    case = sim.info_solver.short_name

    # TODO: easier mechanism to load the last file
    fld = pm.readnek(sorted(sim.path_run.glob(f"{case}0.f?????"))[-1])
    t_end = params.nek.general.end_time = fld.time + 10 * abs(
        params.nek.general.dt
    )  # In phill for some reason dt is negative

    params.nek._write_par(sim.path_run / f"{case}.par")

    sim.make.exec(["run_fg"])

    fld = pm.readnek(sorted(sim.path_run.glob(f"{case}0.f?????"))[-1])
    assert fld.time == t_end
