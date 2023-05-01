import sys
from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import as_completed
from pathlib import Path
from unittest.mock import patch

import pytest

from snek5000.make import _Nek5000Make, snek_make, snek_make_nek


def nek5000_build(config):
    nm = _Nek5000Make()
    return nm.build(config)


def test_nek5000_make(pytestconfig):
    import yaml

    import snek5000
    from snek5000.output.base import Output

    if pytestconfig.getoption("--runslow"):
        # To force rebuild of Nek5000
        (Path(snek5000.get_nek_source_root()) / "bin" / "genbox").unlink()

    snek5000_config = yaml.safe_load(Output.find_configfile().read_text())

    with Pool(max_workers=4) as pool:
        simultaneous_builds = [
            pool.submit(nek5000_build, snek5000_config) for _ in range(4)
        ]
        for future in as_completed(simultaneous_builds):
            assert future.result()


def test_snek_make_help():
    with patch.object(sys, "argv", ["snek-make", "-h"]):
        with pytest.raises(SystemExit):
            snek_make()


def test_snek_make_no_rule(sim_data, monkeypatch):
    monkeypatch.chdir(sim_data)
    with patch.object(sys, "argv", ["snek-make"]):
        with pytest.raises(SystemExit):
            snek_make()


def test_snek_make_clean(sim_data, monkeypatch):
    monkeypatch.chdir(sim_data)
    with patch.object(sys, "argv", ["snek-make", "clean"]):
        snek_make()


def test_snek_make_nek_list():
    with patch.object(sys, "argv", ["snek-make-nek", "--list"]):
        with pytest.raises(SystemExit):
            snek_make_nek()


def test_snek_make_nek_default():
    with patch.object(sys, "argv", ["snek-make-nek"]):
        snek_make_nek()


def test_snek_make_nek_clean_nek():
    with patch.object(sys, "argv", ["snek-make-nek", "--clean-git"]):
        snek_make_nek()


def test_snek_make_nek_genmap():
    with patch.object(sys, "argv", ["snek-make-nek", "bin/genmap"]):
        snek_make_nek()
