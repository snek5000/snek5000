import tempfile
from pathlib import Path

import pytest

from snek5000.log import logger
from snek5000.params import (
    Parameters,
    _as_nek_value,
    _as_python_value,
    _save_par_file,
    _str_par_file,
    complete_params_from_par_file,
)
from snek5000.util import init_params


@pytest.mark.parametrize("input_value", (True, False, None, "a string", 1, 3.14, "nan"))
def test_python_value_roundtrip(input_value):
    roundtrip_python_nek = _as_python_value(_as_nek_value(input_value))
    assert input_value == roundtrip_python_nek


@pytest.mark.parametrize(
    ("input_value", "equivalent"),
    zip(("yes", "no", "42", "2.71"), (True, False, 42, 2.71)),
)
def test_python_value_roundtrip_evaluated(input_value, equivalent):
    roundtrip_python_nek = _as_python_value(_as_nek_value(input_value))
    assert input_value != roundtrip_python_nek == equivalent


@pytest.mark.parametrize(
    ("input_value", "equivalent"),
    zip(("True", "False", "42", "2.71"), ("yes", "no", 42, 2.71)),
)
def test_nek_value_roundtrip_evaluated(input_value, equivalent):
    roundtrip_nek_python = _as_nek_value(_as_python_value(input_value))
    assert input_value != roundtrip_nek_python == equivalent


def save_par_file_and_read(params, path):
    _save_par_file(params, path)
    with open(path) as file:
        return file.read()


def test_empty_params():
    Parameters(tag="empty")


def test_simul_params():
    from snek5000.solvers.base import Simul

    tmp_dir = Path(tempfile.mkdtemp("snek5000", __name__))

    # create params different from the default params
    params = Simul.create_default_params()
    params.nek.general.dt = 2.0

    path_par = tmp_dir / "tmp.par"
    txt = save_par_file_and_read(params, path_par)
    assert txt

    params1 = Simul.create_default_params()
    complete_params_from_par_file(params1, path_par)

    assert params1.nek.general.dt == params.nek.general.dt

    txt1 = save_par_file_and_read(params1, tmp_dir / "tmp1.par")

    assert txt == txt1


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

    tmp_dir = Path(tempfile.mkdtemp("snek5000", __name__))

    par1 = save_par_file_and_read(params, tmp_dir / "tmp1.par")

    params_xml = Path(params._save_as_xml(str(tmp_dir / "params_simul.xml")))

    try:
        from snek5000.params import Parameters

        nparams = Parameters(tag="params", path_file=params_xml)
    except ValueError:
        # NOTE: used to raise an error, now testing experimentally
        pass
    #  else:
    #      raise ValueError("Parameters(path_file=...) worked unexpectedly.")

    nparams = Simul.load_params_from_file(path_xml=params_xml)

    par2 = save_par_file_and_read(nparams, tmp_dir / "tmp2.par")

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


def test_user_params():
    tmp_dir = Path(tempfile.mkdtemp("snek5000", __name__))

    def complete_create_default_params(p):
        if hasattr(p.nek.general, "_recorded_user_params"):
            p.nek.general._recorded_user_params.clear()
        p._set_attribs({"prandtl": 0.71, "rayleigh": 1.8e8})
        p._record_nek_user_params({"prandtl": 1, "rayleigh": 2})
        p._set_child("output")
        p.output._set_child("other", {"write_interval": 100})
        p.output.other._record_nek_user_params({"write_interval": 10}, overwrite=True)

        with pytest.raises(ValueError):
            p._change_index_userparams({2: "prandtl"})

        with pytest.raises(ValueError):
            p._change_index_userparams({5: "foo"})

        p._change_index_userparams({2: "prandtl", 1: "rayleigh"})

    from snek5000.solvers.base import Simul

    params = Simul.create_default_params()
    complete_create_default_params(params)

    assert params.nek.general._recorded_user_params == {
        2: "prandtl",
        1: "rayleigh",
        10: "output.other.write_interval",
    }

    params.prandtl = 2
    params.rayleigh = 2e8
    params.output.other.write_interval = 1000

    path_par = tmp_dir / "tmp.par"
    _save_par_file(params, path_par)

    params1 = Simul.create_default_params()
    complete_create_default_params(params1)

    complete_params_from_par_file(params1, path_par)

    assert params1.prandtl == params.prandtl
    assert params1.rayleigh == params.rayleigh
    assert params1.output.other.write_interval == params.output.other.write_interval


def test_str_par_file(sim, tmp_path):
    path = tmp_path / "test.par"
    par_save_par_file = save_par_file_and_read(sim.params, path)
    par_str_par_file = _str_par_file(sim.params)

    assert par_save_par_file == par_str_par_file
