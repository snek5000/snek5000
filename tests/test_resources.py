from pathlib import Path

import snek5000
from snek5000.resources import get_base_template, get_base_templates


def test_get_nek_source_root():
    assert snek5000.get_nek_source_root()


def test_resource():
    assert snek5000.get_snek_resource("nek5000.smk")
    assert snek5000.get_snek_resource("default_configfile.yml")


def test_base_template():
    name = "compile.sh.j2"
    template = get_base_template(name)
    assert Path(template.filename).name == name


def test_base_templates():
    assert len(get_base_templates()) == 3
