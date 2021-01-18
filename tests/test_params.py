import tempfile
from io import StringIO
from pathlib import Path

from snek5000.log import logger
from snek5000.params import Parameters
from snek5000.util import init_params


def test_empty_params():
    params = Parameters(tag="empty")
    params._write_par()


def test_simul_params():
    from snek5000.solvers.base import Simul

    params = Simul.create_default_params()

    buffer = StringIO()
    params.nek._write_par(buffer)
    params.nek._read_par(buffer)
    buffer2 = StringIO()
    params.nek._write_par(buffer2)

    assert buffer.getvalue() == buffer2.getvalue()


def test_oper_params(oper):
    from snek5000.operators import Operators

    params = init_params(Operators)
    logger.debug(params.oper.max)
    logger.debug(params.oper.max._doc)
    logger.debug(params.oper.elem)
    logger.debug(params.oper.elem._doc)


def test_par_xml_match():
    from phill.solver import Simul

    params = Simul.create_default_params()
    output1 = StringIO()
    params.nek._write_par(output1)

    tmp_dir = Path(tempfile.mkdtemp("snek5000", __name__))
    params_xml = params._save_as_xml(str(tmp_dir / "params_simul.xml"))

    try:
        from snek5000.params import Parameters

        nparams = Parameters(tag="params", path_file=params_xml)
    except ValueError:
        # NOTE: used to raise an error, now testing experimentally
        pass
    #  else:
    #      raise ValueError("Parameters(path_file=...) worked unexpectedly.")

    nparams = Simul.load_params_from_file(path_xml=params_xml)
    output2 = StringIO()
    nparams.nek._write_par(output2)

    par1 = output1.getvalue()
    par2 = output2.getvalue()
    output1.close()
    output2.close()

    def format_sections(params):
        par = params.nek._par_file

        # no options in the section
        for section_name in par.sections():
            if not par.options(section_name):
                par.remove_section(section_name)

        return sorted(par.sections())

    assert format_sections(params) == format_sections(nparams)

    def format_par(text):
        """Sort non-blank lines"""
        from ast import literal_eval

        ftext = []
        for line in text.splitlines():
            # not blank
            if line:
                # Uniform format for literals
                if " = " in line:
                    key, value = line.split(" = ")
                    try:
                        line = " = ".join([key, str(literal_eval(value))])
                    except (SyntaxError, ValueError):
                        pass

                ftext.append(line)

        return sorted(ftext)

    assert format_par(par1) == format_par(par2)
