import pytest

from snek5000 import load_simul


@pytest.mark.parametrize("session_id", (0, 1))
def test_load_simul_error(sim_data, session_id):
    sim = load_simul(sim_data / f"session_{session_id:02d}")
    assert sim.params.output.session_id == session_id


@pytest.mark.parametrize("session_id", (0, 1))
def test_load_simul_session(sim_data, session_id):
    sim = load_simul(sim_data, session_id=session_id)
    assert sim.params.output.session_id == session_id
