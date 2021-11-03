import pytest

from snek5000 import load_simul


def test_load_simul_error(sim_data):
    with pytest.raises(ValueError):
        load_simul(sim_data / "session_00")


def test_load_simul_session(sim_data):
    sim = load_simul(sim_data, session_id=0)
    assert sim.params.output.session_id == 0
