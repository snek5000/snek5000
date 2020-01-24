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
    from eturb.solvers.abl import Simul

    params = Simul.create_default_params()
    params.output.sub_directory = "test"
    return Simul(params)


@pytest.fixture(scope="session")
def oper():
    from eturb.params import Parameters
    from eturb.operators import Operators as Class

    params = Parameters(tag="params")
    Class._complete_params_with_default(params)
    return Class(params=params)
