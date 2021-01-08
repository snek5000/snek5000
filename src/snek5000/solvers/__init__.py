"""
Solver framework

.. autosummary::
   :toctree:

   base
   kth

"""
from functools import partial

from fluidsim_core import loader

available_solvers = partial(loader.available_solvers, entrypoint_grp="snek5000.solvers")
available_solvers.__doc__ = """\
Returns a dictionary of all registered solvers registered as an entrypoint.
"""

import_cls_simul = partial(loader.import_cls_simul, entrypoint_grp="snek5000.solvers")
import_cls_simul.__doc__ = """Import the Simul class of a solver."""
