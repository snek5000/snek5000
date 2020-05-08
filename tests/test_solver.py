from snek5000.solvers.base import Simul


def test_init():
    params = Simul.create_default_params()
    Simul(params)
