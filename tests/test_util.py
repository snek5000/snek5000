import os
import shutil

from snek5000 import util


def test_activate_paths():
    # Remove Nek5000/bin from PATH for the sake of the test
    os.environ["PATH"] = ":".join(
        path for path in os.getenv("PATH").split(":") if "Nek5000/bin" not in path
    )
    assert shutil.which("makenek") is None, "Nek5000/bin is globally available?!"

    util.activate_paths()
    assert shutil.which("makenek"), "Nek5000/bin is not included in the PATH"
