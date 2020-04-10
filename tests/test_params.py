import tempfile
from io import StringIO
from pathlib import Path

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


def  test_par_xml_match():
    from eturb.solvers.abl import Simul

    params = Simul.create_default_params()
    output1 = StringIO()
    params.nek._write_par(output1)

    tmp_dir = Path(tempfile.mkdtemp("eturb", __name__))
    params_xml = params._save_as_xml(str(tmp_dir / "params.xml"))

    from eturb.params import Parameters
    nparams = Parameters(tag="params", path_file=params_xml)
    output2 = StringIO()
    nparams.nek._write_par(output2)

    par1 = output1.getvalue()
    par2 = output2.getvalue()
    output1.close()
    output2.close()
    assert par1 == par2
