import pytest


def pytest_addoption(parser):
    # https://pytest.readthedocs.io/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


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
