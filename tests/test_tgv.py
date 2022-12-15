import pandas as pd


def test_tgv(sim_tgv_executed):
    sim = sim_tgv_executed

    df = sim.output.spatial_means.load()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 2
