def test_package_canonical(sim_canonical):
    sim = sim_canonical
    assert sim.make.exec(["compile"])
