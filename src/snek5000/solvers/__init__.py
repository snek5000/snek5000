"""
Solver framework

.. autosummary::
   :toctree:

   base
   kth

"""
import importlib
from functools import partial
from pathlib import Path
from pkgutil import ModuleInfo
from types import ModuleType

from fluidsim_core import loader

from ..log import logger

available_solvers = partial(loader.available_solvers, entrypoint_grp="snek5000.solvers")
available_solvers.__doc__ = """\
Returns a dictionary of all registered solvers registered as an entrypoint.
"""

import_cls_simul = partial(loader.import_cls_simul, entrypoint_grp="snek5000.solvers")
import_cls_simul.__doc__ = """Import the Simul class of a solver."""


def is_package(module):
    """Checks if a module is a package or not. As of PEP 451 this information
    is also available on the module’s __spec__.submodule_search_locations
    attribute, which will not be None for packages.

    Parameters
    ----------
    module: str or module

    Returns
    -------
    bool

    """
    if isinstance(module, str):
        spec = importlib.util.find_spec(module)
    elif isinstance(module, ModuleType):
        spec = module.__spec__
    elif isinstance(module, ModuleInfo):
        return module.ispkg
    else:
        raise ValueError(f"Cannot process {type(module)}")

    return spec.submodule_search_locations is not None


def get_solver_package(name_solver):
    """Return name of the solver package by checking the ``snek5000.solvers``
    entrypoint group.

    Parameters
    ----------
    name_solver: str
        Short name of the solver

    Returns
    -------
    str

    """
    entrypoint = available_solvers()[name_solver]
    module = entrypoint.module_name
    if is_package(module):
        return module
    else:
        return module.rpartition(".")[0]


def get_solver_short_name(path_dir):
    """Detects short name of the solver from ``info_solver.xml`` if present or
    the path.

    Parameters
    ----------
    path_dir: path-like
        Path to a simulation directory

    Returns
    -------
    short_name: str

    """
    info_solver_xml = path_dir / "info_solver.xml"
    if info_solver_xml.exists():
        from snek5000.info import InfoSolverNek

        info_solver = InfoSolverNek(path_file=info_solver_xml)
        short_name = info_solver.short_name
    else:
        logger.warning(f"The {info_solver_xml} file is missing!")
        short_name = path_dir.absolute().name.split("_")[0]

    return short_name


def load_params(path_dir="."):
    """Load a :class:`snek5000.params.Parameters` instance from `path_dir`.

    Parameters
    ----------
    path_dir : str or path-like
        Path to a simulation directory.

    Returns
    -------
    params: :class:`snek5000.params.Parameters`

    """
    path_dir = Path(path_dir)
    short_name = get_solver_short_name(path_dir)
    Simul = import_cls_simul(short_name)

    return Simul.load_params_from_file(
        path_xml=path_dir / "params_simul.xml", path_par=path_dir / f"{short_name}.par"
    )
