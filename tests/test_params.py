from eturb.params import Parameters
from eturb.solvers.base import Simul


def test_empty_params():
    params = Parameters(tag="empty")
    params._write_par()


def test_simul_params():
    params = Simul.create_default_params()
    params._write_par()
