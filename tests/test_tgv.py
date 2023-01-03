import pandas as pd
import pytest


@pytest.mark.slow
def test_tgv(sim_tgv_executed):
    sim = sim_tgv_executed

    df = sim.output.spatial_means.load()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 2
    sim.output.spatial_means.plot()

    df = sim.output.remaining_clock_time.load()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2

    sim.output.remaining_clock_time.plot()
