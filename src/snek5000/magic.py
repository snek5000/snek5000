"""IPython magic extensions
===========================

Usage example in an IPython console:

.. code-block:: ipython

   In [1]: %load_ext snek5000.magic
   WARNING  Activating this magic involves dirty monkey-patching of fluidsim.magic

   In [2]: %snek5000 abl
   INFO     Reading baseline parameters from /home/avmo/src/exabl/snek5000/src/abl/abl.par
   Created Simul class and default parameters for abl -> Simul, params

   In [3]: sim = Simul(params)

"""
import pkgutil
from importlib import import_module

from fluidsim import magic as fluidsim_magic
from IPython.core import magic_arguments
from IPython.core.magic import line_magic, magics_class

from .log import logger


def available_solver_keys(package):
    package = import_module(package)
    modules = [
        mod.name for mod in pkgutil.walk_packages(package.__path__) if not mod.ispkg
    ]
    return modules


def import_simul_class_from_key(key, package):
    solver = import_module(f"{package}.{key}")
    return solver.Simul


# Monkey patch
fluidsim_magic.available_solver_keys = available_solver_keys
fluidsim_magic.import_simul_class_from_key = import_simul_class_from_key


@magics_class
class EturbMagics(fluidsim_magic.FluidsimMagics):
    @magic_arguments.magic_arguments()
    @magic_arguments.argument("solver", nargs="?", default="")
    @magic_arguments.argument("-f", "--force-overwrite", action="store_true")
    @line_magic
    def snek5000(self, line):
        super().fluidsim(line)


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    logger.warning(
        "Activating this magic involves dirty monkey-patching of fluidsim.magic"
    )
    magics = EturbMagics(ipython, "snek5000.solvers")
    ipython.register_magics(magics)
