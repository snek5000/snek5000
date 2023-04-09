from snek5000 import load_for_restart


@pytest.mark.slow
def test_make_run(sim):
    # Run in foreground
    assert sim.make.exec("run_fg", nproc=2)

    # test outputs
    print(sim.output.print_stdout.path_file)
    df = sim.output.print_stdout.load()

    # number of time steps executed, see conftest.py
    assert df.dt.size == sim.params.nek.general.num_steps

    # check if simulation can be restarted
    # TODO: try restart with modified params
    _ = load_for_restart(sim.path_run, use_start_from=-1)
