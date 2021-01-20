from snek5000 import load_simul
from snek5000.solvers import available_solvers, import_cls_simul


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

    assert Simul is import_cls_simul("phill")
    params = Simul.create_default_params()
    sim1 = Simul(params)
    sim2 = load_simul(sim1.path_run)
    assert isinstance(sim1, Simul) and isinstance(sim2, Simul)


def test_output(sim_data):
    sim = load_simul(sim_data)

    assert (
        sim.output.print_stdout.file.exists()
    ), "Cannot find .log file for print_stdout"
    assert sim.output.phys_fields.path_run.exists(), "Cannot initialize phys_fields"
