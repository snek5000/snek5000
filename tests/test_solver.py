from snek5000 import load_simul
from snek5000.solvers import available_solvers, import_solver


def test_entrypoints():
    solvers = available_solvers()
    assert "nek" in solvers
    assert "kth" in solvers
    assert "phill" in solvers


def test_init_base():
    from snek5000.solvers.base import Simul

    params = Simul.create_default_params()
    Simul(params)


def test_init_kth():
    from snek5000.solvers.kth import Simul

    params = Simul.create_default_params()
    Simul(params)


def test_import_solver():
    from phill.solver import Simul

    assert Simul is import_solver("phill")
    params = Simul.create_default_params()
    sim1 = Simul(params)
    sim2 = load_simul(sim1.path_run)
    assert isinstance(sim1, Simul) and isinstance(sim2, Simul)
