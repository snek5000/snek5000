# isort: skip_file
"""
A Pythonic frontend to Nek5000.

**Sub-packages**

.. autosummary::
   :toctree:

   assets
   output
   solvers
   util

**Modules**

.. autosummary::
   :toctree:

   info
   log
   magic
   make
   operators
   params

"""
try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources
import os
from pathlib import Path

from fluiddyn.util import mpi  # noqa: F401

from ._version import __version__  # noqa: F401
from .log import logger  # noqa: F401


def source_root():
    """Path of Nek5000 source code."""
    if os.getenv("SOURCE_ROOT"):
        logger.warning(
            "The environment variable "
            "SOURCE_ROOT is deprecated in v19, use NEK_SOURCE_ROOT instead."
        )

    with resources.path(__name__, "__init__.py") as f:
        root = f.parent

    nek5000 = os.path.expandvars(
        os.path.expanduser(
            os.getenv("NEK_SOURCE_ROOT", str((root / "../../lib/Nek5000").absolute()))
        )
    )
    if not os.path.exists(nek5000):
        logger.error("NEK_SOURCE_ROOT: " + nek5000)
        raise IOError(
            "Cannot find Nek5000 source code. Use environment variable "
            "NEK_SOURCE_ROOT to point to Nek5000 top level directory."
        )
    return nek5000


def get_asset(asset_name):
    """Fetches path of an asset from subpackage ``snek5000.assets``."""
    asset = next(resources.path("snek5000.assets", asset_name).gen)
    return asset


def load_simul(path_dir):
    path_dir = Path(path_dir)

    from warnings import warn

    info_solver_xml = path_dir / "info_solver.xml"
    if info_solver_xml.exists():
        from snek5000.info import InfoSolverNek

        info_solver = InfoSolverNek(path_file=info_solver_xml)
        solver = info_solver.short_name
    else:
        warn(f"The {info_solver_xml} file is missing!")
        solver = path_dir.name.split("_")[0]

    # Load simulation class
    from snek5000.solvers import import_cls_simul

    Simul = import_cls_simul(solver)

    # Load parameters
    from snek5000.params import Parameters

    params = Parameters._load_params_simul(path_dir)

    # try:
    #     params_par = next(path_dir.glob("*.par"))
    # except StopIteration:
    #     warn(f"The {path_dir}/*.par file is missing!")
    #     params_par = None
    #
    # params_xml = path_dir / "params_simul.xml"
    # params = Simul.load_params_from_file(path_xml=params_xml, path_par=params_par)
    # Modify parameters prior to loading
    params.NEW_DIR_RESULTS = False
    params.output.HAS_TO_SAVE = False
    params.path_run = path_dir
    sim = Simul(params)
    return sim


from .util.smake import append_debug_flags, ensure_env  # noqa: F401, E402
