"""
A Pythonic frontend to Nek5000.

**Sub-packages**

.. autosummary::
   :toctree:

   output
   solvers

**Modules**

.. autosummary::
   :toctree:

   info
   log
   magic
   make
   operators
   params
   util

"""
import importlib.resources
import os

from fluiddyn.util import mpi  # noqa: F401

from . import util  # noqa: F401
from ._version import __version__  # noqa: F401
from .log import logger  # noqa: F401


def source_root():
    """Path of Nek5000 source code."""
    with importlib.resources.path(__name__, "__init__.py") as f:
        root = f.parent
    return os.getenv("SOURCE_ROOT", str((root / "../../lib/Nek5000").absolute()))


def get_asset(asset_name):
    """Fetches path of an asset from subpackage ``snek5000.assets``."""
    asset = next(importlib.resources.path("snek5000.assets", asset_name).gen)
    return asset
