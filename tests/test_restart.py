import pytest
import xarray as xr
from pymech.neksuite.field import read_header

import snek5000
from snek5000.output import _make_path_session
from snek5000.params import load_params
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
    session = _make_path_session(sim_data, 1)
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
    _make_path_session(sim_data, 1)
    [restart.unlink() for restart in sim_data.glob("rs6*")]

    assert get_status(sim_data).code == 206


@pytest.mark.parametrize("prefix_dir", ("phill_", "undefined_solver"))
def test_restart_error(tmpdir_factory, prefix_dir):
    tmpdir = tmpdir_factory.mktemp(prefix_dir)
    with pytest.raises(SnekRestartError):
        load_for_restart(tmpdir)


@pytest.mark.slow
def test_restart(sim_executed):
    # In real workflows, to pre load data in preperation for restart, use:
    # >>> sim_executed = snek5000.load()
    fld_file = sim_executed.output.get_field_file()

    header = read_header(fld_file)
    params, Simul = load_for_restart(
        sim_executed.path_run, use_start_from=fld_file.name
    )

    assert params.output.HAS_TO_SAVE
    assert not params.NEW_DIR_RESULTS

    t_end = params.nek.general.end_time = header.time + 10 * abs(
        params.nek.general.dt
    )  # In phill for some reason dt is negative

    sim = Simul(params)
    sim.make.exec("run_fg")

    header = read_header(sim.output.get_field_file())
    assert header.time == t_end

    header = read_header(sim.output.get_field_file(t_approx=t_end))
    assert header.time == t_end

    # check if params_simul.xml is updated
    params_in_filesystem = load_params(sim_executed.path_run)
    assert params.output.session_id == params_in_filesystem.output.session_id


@pytest.mark.slow
def test_restart_new_dir_results(sim_executed):
    params, Simul = load_for_restart(
        sim_executed.path_run, use_start_from=True, new_dir_results=True
    )
    assert params.output.HAS_TO_SAVE
    assert params.NEW_DIR_RESULTS
    assert params.nek.general.start_from == "init_state.restart"
    sim = Simul(params)
    fld_file = sim_executed.output.get_field_file()
    sim.create_symlink_start_from_file(fld_file)


@pytest.mark.slow
def test_restart_new_dir_results_checkpoint(sim_cbox_executed):
    params, Simul = load_for_restart(
        sim_cbox_executed.path_run, use_checkpoint=1, new_dir_results=True
    )
    assert params.output.HAS_TO_SAVE
    assert params.NEW_DIR_RESULTS
    assert params.nek.chkpoint.chkp_fnumber == 1
    assert params.nek.chkpoint.read_chkpt is True
    sim = Simul(params)
    sim.create_symlinks_checkpoint_files(sim_cbox_executed.output.path_run)


def test_phys_fields_uninit(sim):
    """Should error if trying to load / get_var without executing init_reader."""
    with pytest.raises(
        RuntimeError, match="The reader and the method has not initialized yet."
    ):
        sim.output.phys_fields.load()

    with pytest.raises(
        RuntimeError, match="The reader and the method has not initialized yet."
    ):
        sim.output.phys_fields.get_var()


@pytest.mark.parametrize("reader", (True, "pymech_stats"))
def test_load_with_phys_fields(sim, reader):
    sim2 = snek5000.load(sim.path_run, reader=reader)
    with pytest.raises(FileNotFoundError):
        sim2.output.phys_fields.load()

    with pytest.raises(FileNotFoundError):
        sim2.output.phys_fields.get_var("ux")


def test_load_wrong_phys_fields_reader(sim):
    with pytest.raises(ValueError, match="params.output.phys_fields.available_readers"):
        snek5000.load(sim.path_run, reader=1.0)


pymech_issue = (
    "Pymech does not support non-box meshes, and snek5000-phill has "
    "such a geometry: https://github.com/eX-Mech/pymech/issues/31"
)


@pytest.mark.slow
@pytest.mark.xfail(NotImplementedError, reason=pymech_issue)
def test_phys_fields_load_all(sim_executed):
    sim_executed.output.phys_fields.init_reader()
    ds = sim_executed.output.phys_fields.load(index="all")
    assert isinstance(ds, xr.Dataset)


@pytest.mark.slow
@pytest.mark.xfail(NotImplementedError, reason=pymech_issue)
def test_phys_fields_load_stats(sim_executed):
    sim_executed.output.phys_fields.change_reader("pymech_stats")
    ds = sim_executed.output.phys_fields.load(index="*0")
    assert isinstance(ds, xr.Dataset)


@pytest.mark.slow
def test_phys_fields(sim_executed):
    sim_executed.output.phys_fields.init_reader()
    try:
        ds = sim_executed.output.phys_fields.load()
    except NotImplementedError:
        pytest.xfail(reason=pymech_issue)
    else:
        assert isinstance(ds, xr.Dataset)
