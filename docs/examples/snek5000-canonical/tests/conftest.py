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
    from snek5000_canonical.solver import Simul

    params = Simul.create_default_params()
    params.output.sub_directory = "test_snek5000-canonical"

    params.nek.general.stop_at = "numSteps"
    params.nek.general.num_steps = 9

    params.nek.general.write_interval = 5

    params.oper.nproc_min = 2
    params.oper.nproc_max = 12
    params.oper.nx = params.oper.ny = params.oper.nz = 3
    params.oper.elem.order = params.oper.elem.order_out = 6

    params.nek.stat.av_step = 2
    params.nek.stat.io_step = 4

    return Simul(params)
