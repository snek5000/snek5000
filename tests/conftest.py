import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pymech
import pytest

from snek5000 import load
from snek5000.util.gfortran_log import log_matches


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


def modif_test_params(params):
    params.output.sub_directory = "tests_snek5000"
    params.oper.nproc_min = 2


@pytest.fixture(scope="session")
def jinja_env():
    import jinja2

    env = jinja2.Environment(
        loader=jinja2.PackageLoader("snek5000", "resources"),
        undefined=jinja2.StrictUndefined,
    )
    return env


@pytest.fixture(scope="session")
def sim():
    from phill.solver import Simul

    params = Simul.create_default_params()
    modif_test_params(params)

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
    modif_test_params(params)
    set_params_oper2d(params)
    return Simul(params)


@pytest.fixture(scope="module")
def sim_canonical():
    from snek5000_canonical.solver import Simul

    params = Simul.create_default_params()
    modif_test_params(params)
    return Simul(params)


@pytest.fixture(scope="session")
def sim_executed():
    from phill.solver import Simul

    params = Simul.create_default_params()
    modif_test_params(params)

    params.nek.general.stop_at = "endTime"
    params.nek.general.end_time = 10 * abs(params.nek.general.dt)
    params.nek.general.write_interval = 5

    params.oper.nproc_max = 12
    params.oper.nx = params.oper.ny = params.oper.nz = 3
    params.oper.elem.order = params.oper.elem.order_out = 8

    params.nek.stat.av_step = 2
    params.nek.stat.io_step = 4

    sim = Simul(params)
    assert sim.make.exec("run_fg"), "phill simulation failed"
    return sim


@contextmanager
def unset_snek_debug():
    old_snek_debug = os.environ.pop("SNEK_DEBUG", None)
    try:
        yield
    finally:
        if old_snek_debug is not None:
            os.environ["SNEK_DEBUG"] = old_snek_debug


@pytest.fixture(scope="session")
def sim_cbox_executed():
    from snek5000_cbox.solver import Simul

    params = Simul.create_default_params()
    modif_test_params(params)
    params.Ra_side = 1.83e08

    params.nek.general.stop_at = "numSteps"
    params.nek.general.dt = 1e-3
    params.nek.general.num_steps = 12
    params.nek.general.write_interval = 3

    params.oper.nproc_max = 12
    params.oper.dim = 2
    params.oper.nx = params.oper.ny = 8

    coords = [(0.5, 0.5)]
    params.output.history_points.write_interval = 2
    params.output.history_points.coords = coords
    params.oper.max.hist = len(coords) + 1

    sim = Simul(params)
    sim.output.write_snakemake_config(custom_env_vars={"FOO": 1})

    with unset_snek_debug():
        if not sim.make.exec("compile"):
            build_log = Path(sim.output.path_run) / "build.log"
            log_matches(build_log, levels=["Error"])
            raise RuntimeError("cbox compilation failed")

    if not sim.make.exec("run_fg", nproc=2):
        with open(Path(sim.output.path_run) / "cbox.log") as file:
            print(file.read())
        raise RuntimeError("cbox simulation failed")
    return sim


@pytest.fixture(scope="session")
def sim_cbox_executed_readonly(sim_cbox_executed):
    path_run = Path(sim_cbox_executed.output.path_run)
    with tempfile.TemporaryDirectory(suffix="snek5000_cbox_executed") as tmp_dir:
        path_readonly_sim = Path(tmp_dir) / path_run.name
        shutil.copytree(path_run, path_readonly_sim)

        for path in path_readonly_sim.rglob("*"):
            mod = 0o444
            if path.is_dir():
                mod = 0o544
            path.chmod(mod)

        sim = load(path_readonly_sim)
        yield sim

        for path in path_readonly_sim.rglob("*"):
            mod = 0o644
            if path.is_dir():
                mod = 0o744
            path.chmod(mod)


@pytest.fixture(scope="session")
def sim_tgv_executed():
    from snek5000_tgv.solver import Simul

    params = Simul.create_default_params()
    modif_test_params(params)

    params.oper.nx = params.oper.ny = params.oper.nz = 6
    params.oper.elem.order = params.oper.elem.order_out = 6

    params.nek.velocity.residual_tol = 1e-07
    params.nek.pressure.residual_tol = 1e-05

    params.nek.general.end_time = 1
    params.nek.general.dt = -1
    params.nek.general.target_cfl = 1.4
    params.nek.general.extrapolation = "OIFS"

    params.nek.general.write_control = "runTime"
    params.nek.general.write_interval = 0.5

    params.output.spatial_means.write_interval = 0.5
    params.output.remaining_clock_time.period_save_in_seconds = 1.0

    sim = Simul(params)
    if not sim.make.exec("run_fg", nproc=2):
        with open(Path(sim.output.path_run) / "cbox.log") as file:
            print(file.read())
        raise RuntimeError("tgv simulation failed")

    return sim


def create_fake_nek_files(path_dir, name_solver, nb_files=1):
    nx = 2
    ny = 4
    nz = 6
    nx_elem = ny_elem = nz_elem = 2

    hexa_data = pymech.core.HexaData(
        ndim=3,
        nel=nx_elem * ny_elem * nz_elem,
        lr1=(nx, ny, nz),
        var=(3, 3, 1, 1, 0),
    )
    hexa_data.wdsz = 8
    hexa_data.istep = 0
    hexa_data.endian = sys.byteorder

    x1d = np.linspace(0, 1, nx)
    y1d = np.linspace(0, 1, ny)
    z1d = np.linspace(0, 1, nz)

    y3d, z3d, x3d = np.meshgrid(y1d, z1d, x1d)
    assert y3d.shape == (nz, ny, nx)

    ielem = 0
    for iz_elem in range(nz_elem):
        for iy_elem in range(ny_elem):
            for ix_elem in range(nx_elem):
                elem = hexa_data.elem[ielem]
                ielem += 1
                elem.pos[0] = x3d + ix_elem
                elem.pos[1] = y3d + iy_elem
                elem.pos[2] = z3d + iz_elem
                elem.vel.fill(1)

    time = 2.0
    for it in range(nb_files):
        hexa_data.time = time
        pymech.writenek(path_dir / f"{name_solver}0.f{it:05d}", hexa_data)
        time += 0.5


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
            create_fake_nek_files(path_session, "phill")

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
