"""
Python package for scripted assistance.

.. autosummary::
   :toctree:

   solvers
   output
   params
   util

"""
from fluiddyn.util import mpi

from . import util
from ._version import __version__
from .log import logger
