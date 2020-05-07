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
from fluiddyn.util import mpi  # noqa: F401

from . import util  # noqa: F401
from ._version import __version__  # noqa: F401
from .log import logger  # noqa: F401
