import os
import shutil
from collections import defaultdict

import pytest

from snek5000.util.smake import (
    append_debug_flags,
    ensure_env,
    set_compiler_verbosity,
)


def test_ensure_env():
    # Remove Nek5000/bin from PATH for the sake of the test
    os.environ["PATH"] = ":".join(
        path for path in os.getenv("PATH").split(":") if "Nek5000/bin" not in path
    )
    assert shutil.which("makenek") is None, "Nek5000/bin is globally available?!"

    ensure_env()
    assert shutil.which("makenek"), "Nek5000/bin is not included in the PATH"


@pytest.mark.parametrize("verbosity", (0, 1, 2))
def test_verbosity(verbosity):
    config = defaultdict(str)
    set_compiler_verbosity(config, verbosity)
    if not verbosity:
        assert " -w " in config["FFLAGS"]
        assert " -w " in config["CFLAGS"]
    elif verbosity == 1:
        assert " -w " not in config["FFLAGS"]
        assert " -w " not in config["CFLAGS"]
        assert " -Wall " not in config["FFLAGS"]
        assert " -Wall " not in config["CFLAGS"]
    elif verbosity == 2:
        assert " -Wall " in config["FFLAGS"]
        assert " -Wall " in config["CFLAGS"]


@pytest.mark.parametrize("warnings", (True, False))
def test_debug_flags(warnings):
    debug_state = os.getenv("SNEK_DEBUG", "")
    os.environ["SNEK_DEBUG"] = "1"

    config = defaultdict(str)
    append_debug_flags(config)

    assert all("-O0 -g" in config[k] for k in ("CFLAGS", "FFLAGS"))

    os.environ["SNEK_DEBUG"] = debug_state
