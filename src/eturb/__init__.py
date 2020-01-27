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
from fluiddyn.util import mpi

from . import util
from ._version import __version__
from .log import logger
