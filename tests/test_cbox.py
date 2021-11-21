import pytest
import xarray as xr

from snek5000 import load
from snek5000.util import repeat


@pytest.mark.slow
def test_history_points(sim_cbox_executed):
    sim = sim_cbox_executed
    params = sim.params
    p_hist = params.output.history_points

    hist_points = sim.output.history_points
    coords, df = hist_points.load()

    assert len(coords) == len(p_hist.coords)
    assert len(df) == 1 + params.nek.general.num_steps // p_hist.write_interval

    hist_points.plot("temperature")

    # let's tweak the cbox.his to mimic a new data point
    with open(hist_points.path_file, "r") as file:
        file.readline()
        for _ in repeat(len(p_hist.coords)):
            file.readline()

        line_data = file.readline()
    with open(hist_points.path_file, "a") as file:
        file.write(f"{line_data}\nbad\n")

    hist_points.plot_1point(0, "temperature", tmin=0, tmax=1)


@pytest.mark.slow
def test_loadsimul_phys_fields(sim_cbox_executed):
    sim = load(sim_cbox_executed.path_run)

    ux = sim.output.phys_fields.get_var("ux")
    assert isinstance(ux, xr.DataArray)


@pytest.mark.slow
def test_phys_fields_get_var_before_load(sim_cbox_executed):
    sim = sim_cbox_executed
    sim.output.phys_fields.init_reader()
    ux = sim.output.phys_fields.get_var("ux")
    assert isinstance(ux, xr.DataArray)
