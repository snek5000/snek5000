import sys

import pytest

from snek5000 import load


def test_load(sim_canonical):
    # Reload snek5000_canonical so that the load method would freshly import snek5000_canonical
    # https://stackoverflow.com/a/57851153
    for module in tuple(sys.modules):
        if module.startswith("snek5000_canonical"):
            del sys.modules[module]

    sim2 = load(sim_canonical.path_run, reader="pymech_avg")
    with pytest.raises(IOError, match="no files to open"):
        sim2.output.phys_fields.plot_mean_vel()
    with pytest.raises(IOError, match="No file "):
        sim2.output.remaining_clock_time.load()


@pytest.mark.slow
def test_package_canonical(sim_canonical):
    sim = sim_canonical
    assert sim.make.exec("compile")
