def test_entrypoints():
    from snek5000.solvers import available_solvers

    solvers = available_solvers()
    assert "base" in solvers
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
    from snek5000.solvers import import_solver

    assert Simul is import_solver("phill")
