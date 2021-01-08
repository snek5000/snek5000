"""IPython magic extensions
===========================

Usage example in an IPython console:

.. code-block:: ipython

   In [1]: %load_ext snek5000.magic

   In [2]: %snek abl
   INFO     Reading baseline parameters from /home/avmo/src/exabl/snek5000/src/abl/abl.par
   Created Simul class and default parameters for abl -> Simul, params

   In [3]: sim = Simul(params)

"""
from fluidsim_core.magic import MagicsCore
from IPython.core.magic import line_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments


@magics_class
class SnekMagics(MagicsCore):
    """Magic commands can be loaded in IPython or Jupyter as

    >>> %load_ext fluidsim.magic

    Examples
    --------

    - Magic command %fluidsim or %snek (alias)

    %snek creates the variables `params` and `Simul` for a particular solver.

    Create default parameters for a solver:

    >>> %snek phill

    If a variable `params` already exists, you will be ask if you really want to
    overwrite it. To skip this question:

    >>> %snek phill -f

    List all available solvers and initialized simulation:

    >>> %snek

    - Other fluidsim magic commands

    Quick reference (print this help message):

    >>> %fluidsim_help

    Delete the objects `sim` and `params`:

    >>> %fluidsim_reset

    .. todo::

        - Magic command %fluidsim_load

        %fluidsim_load creates the variables `sim`, `params` and `Simul` from an
        existing simulation.

        Load existing simulation excluding state_phys files:

        >>> %fluidsim_load

        Load existing simulation all options: force overwrite, with state_phys
        files, merging parameters:

        >>> %fluidsim_load -f -s -t -m


    """

    entrypoint_grp = "snek5000.solvers"

    @magic_arguments()
    @argument("solver", nargs="?", default="")
    @argument("-f", "--force-overwrite", action="store_true")
    @line_magic
    def snek(self, line):
        super().fluidsim(line)


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    magics = SnekMagics(ipython)
    ipython.register_magics(magics)
