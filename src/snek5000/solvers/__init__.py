"""
Solver framework

.. autosummary::
   :toctree:

   base
   kth

"""


def available_solvers():
    """Returns a dictionary of all registered solvers registered as an
    entrypoint_.

    _entrypoint: https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata

    """
    import entrypoints

    return entrypoints.get_group_named("snek5000.solvers")


def import_solver(name):
    """Import the Simul class of a solver."""
    solvers = available_solvers()
    module = solvers[name].load()
    return module.Simul
