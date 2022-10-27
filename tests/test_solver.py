import pytest

from snek5000 import load_simul
from snek5000.solvers import available_solvers, import_cls_simul


def test_entrypoints():
    solvers = [entrypoint.name for entrypoint in available_solvers()]
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
        sim.output.print_stdout.path_file.exists()
    ), "Cannot find .log file for print_stdout"
    try:
        sim.output.phys_fields
    except AttributeError as err:
        raise AssertionError("Cannot initialize phys_fields") from err


def test_make_exec_deprecation(sim2d):
    with pytest.deprecated_call():
        sim2d.make.exec(["phill.re2", "phill.ma2"])

    sim2d.make.exec("SESSION.NAME")


def test_init_output():
    from phill.solver import Simul

    params = Simul.create_default_params()

    # init history_points
    coords = params.output.history_points.coords = [
        (0.5, 0.2, 0.5),
        (0.5, 0.8, 0.5),
    ]
    params.oper.max.hist = len(coords) + 1

    sim = Simul(params)

    # tests history_points
    assert sim.output.history_points.path_file.exists()
    coords, df = sim.output.history_points.load()

    assert len(df) == 0
    assert tuple(coords.iloc[-1]) == params.output.history_points.coords[-1]

    with open(sim.output.history_points.path_file, "a") as file:
        file.write(
            "\n".join(
                ["0.0 2.0 2.0 2.0 2.0"] * 2
                + ["0.5 2.0 2.0 2.0 2.0"] * 2
                + ["1.0 2.0 2.0 2.0 2.0\n2.0 2.0\n"]
            )
        )

    sim.output.history_points.plot()
