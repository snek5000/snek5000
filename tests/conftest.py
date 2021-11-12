import shutil
from pathlib import Path

import pytest


def pytest_addoption(parser):
    # https://pytest.readthedocs.io/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")

    try:
        import rich  # noqa

        import snek5000.log

    except ImportError:
        pass
    else:
        # Bug while using rich + pytest: stderr / stdout is too short
        # Inspired from: https://github.com/willmcgugan/rich/issues/1425
        snek5000.log.logger.removeHandler(snek5000.log.handler)

        handler = snek5000.log.create_handler(width=shutil.get_terminal_size().columns)
        snek5000.log.logger.addHandler(handler)


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="session")
def jinja_env():
    import jinja2

    env = jinja2.Environment(
        loader=jinja2.PackageLoader("snek5000", "assets"),
        undefined=jinja2.StrictUndefined,
    )
    return env


@pytest.fixture(scope="session")
def sim():
    from phill.solver import Simul

    params = Simul.create_default_params()
    params.output.sub_directory = "test"

    params.nek.general.stop_at = "numSteps"
    params.nek.general.num_steps = 9
    return Simul(params)


@pytest.fixture(scope="session")
def oper():
    from snek5000.operators import Operators as Class
    from snek5000.util import init_params

    params = init_params(Class)
    params.oper.nx = params.oper.ny = params.oper.nz = 9
    params.oper.nproc_min = 6

    return Class(params=params)


def set_params_oper2d(params):
    params.oper.nx = params.oper.ny = 16
    params.oper.Lx = params.oper.Ly = 1
    params.oper.dim = 2
    params.oper.boundary = ["W"] * 4
    params.oper.boundary_scalars = ["t"] * 2 + ["I"] * 2

    params.oper.nproc_min = 4
    params.oper.nproc_max = 32

    elem = params.oper.elem
    elem.order = elem.order_out = 15
    elem.coef_dealiasing = 1.0 / 1.6
    elem.staggered = False

    params.oper.max.hist = 100


@pytest.fixture(scope="session")
def oper2d():
    from snek5000.operators import Operators as Class
    from snek5000.util import init_params

    params = init_params(Class)
    set_params_oper2d(params)
    return Class(params=params)


@pytest.fixture(scope="session")
def sim2d():
    from phill.solver import Simul

    params = Simul.create_default_params()
    params.output.sub_directory = "test"

    set_params_oper2d(params)
    return Simul(params)


@pytest.fixture(scope="module")
def sim_canonical():
    from snek5000_canonical.solver import Simul

    params = Simul.create_default_params()
    return Simul(params)


@pytest.fixture(scope="module")
def sim_executed():
    from phill.solver import Simul

    params = Simul.create_default_params()
    params.output.sub_directory = "test"

    params.nek.general.stop_at = "endTime"
    params.nek.general.end_time = 10 * abs(params.nek.general.dt)
    params.nek.general.write_interval = 5

    params.oper.nproc_min = 2
    params.oper.nproc_max = 12
    params.oper.nx = params.oper.ny = params.oper.nz = 3

    params.nek.stat.av_step = 4
    params.nek.stat.io_step = 8

    sim = Simul(params)
    assert sim.make.exec(["run_fg"]), "phill simulation failed"
    return sim


@pytest.fixture
def sim_cbox_executed(monkeypatch):
    from snek5000_cbox.solver import Simul

    params = Simul.create_default_params()
    params.output.sub_directory = "test"

    params.nek.general.stop_at = "endTime"
    params.nek.general.dt = 1e-3
    params.nek.general.end_time = 10 * abs(params.nek.general.dt)
    params.nek.general.write_interval = 5

    params.oper.nproc_min = 2
    params.oper.nproc_max = 12
    params.oper.nx = params.oper.ny = params.oper.nz = 3

    coords = [(0.5, 0.5)]
    params.output.history_points.coords = coords
    params.oper.max.hist = len(coords) + 1

    def mock_append_debug_flags(config, warnings):
        pass

    monkeypatch.setattr("snek5000.append_debug_flags", mock_append_debug_flags)
    monkeypatch.setattr(
        "snek5000.util.smake.append_debug_flags", mock_append_debug_flags
    )
    monkeypatch.setattr(
        "snek5000.output.base.append_debug_flags", mock_append_debug_flags
    )

    sim = Simul(params)
    assert sim.make.exec(["run_fg"], resources={"nproc": 2}), "cbox simulation failed"
    return sim


@pytest.fixture(scope="function")
def sim_data(tmpdir_factory):
    """Generate fake simulation data."""
    files = """box.tmp
makefile
makefile_usr.inc
nek5000
phill.box
phill.f
phill.log
phill.ma2
phill.par
phill.re2
phill.usr
rs6phill0.f00001
rs6phill0.f00002
rs6phill0.f00003
SESSION.NAME
SIZE
Snakefile""".splitlines()

    session_files = """
phill0.f00001
""".splitlines()

    path_run = Path(tmpdir_factory.mktemp("phill_sim_data"))

    from snek5000.output import _make_path_session

    for f in files:
        (path_run / f).touch()

    for session_id in range(2):
        path_session = _make_path_session(path_run, session_id)
        path_session.mkdir()
        for f in session_files:
            (path_session / f).touch()

    from phill.solver import Simul

    info = Simul.InfoSolver()
    params = Simul.create_default_params()

    info._save_as_xml(path_run / "info_solver.xml")
    params._set_attrib("path_run", path_run)
    params.output._set_attrib("session_id", session_id)
    params.output._set_attrib("path_session", path_session)
    params._save_as_xml(path_run / "params_simul.xml")

    return path_run


@pytest.fixture(autouse=True, scope="session")
def shared_datadir_remove():
    """Removes empty data directory as a result of pytest-datadir"""
    yield  # Execute all tests
    shared_datadir = Path(__file__).parent.parent / "data"
    if shared_datadir.exists():
        shared_datadir.rmdir()
