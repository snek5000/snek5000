from eturb.params import Parameters
from eturb.util import init_params
from eturb.log import logger


def test_empty_params():
    params = Parameters(tag="empty")
    params._write_par()


def test_simul_params():
    from eturb.solvers.base import Simul

    params = Simul.create_default_params()
    params.nek._write_par()


def test_oper_params(oper):
    from eturb.operators import Operators

    params = init_params(Operators)
    logger.debug(params.oper.max)
    logger.debug(params.oper.max._doc)
    logger.debug(params.oper.elem)
    logger.debug(params.oper.elem._doc)
