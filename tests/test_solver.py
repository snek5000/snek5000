
def test_init_base():
    from snek5000.solvers.base import Simul

    params = Simul.create_default_params()
    Simul(params)


def test_init_kth():
    from snek5000.solvers.kth import Simul

    params = Simul.create_default_params()
    Simul(params)
