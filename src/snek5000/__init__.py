# isort: skip_file
"""
API reference

**Sub-packages**

.. autosummary::
   :toctree:

   assets
   clusters
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


def load_simul(path_dir=".", session_id=None):
    """Loads a simulation

    .. todo::

        Now only the parameters are loaded. Load state too.

    Parameters
    ----------
    path_dir: str or path-like
        Path to a directory containing a simulation. If not provided the
        current directory is used.

    session_id: int
        Indicate which session directory should be used to set
        ``sim.output.path_session``. If not specified it would default to the
        `session_id` and `path_session` values last recorded in the
        `params_simul.xml` file


    .. hint::

        An common use case of ``session_id`` parameter is to load field
        files from old sessions using the :meth:`sim.output.get_field_file
        <snek5000.output.base.Output.get_field_file>` method

    """
    path_dir = Path(path_dir)

    # Load simulation class
    from snek5000.solvers import import_cls_simul, get_solver_short_name

    short_name = get_solver_short_name(path_dir)
    if short_name == "session" and not (path_dir / "info_solver.xml").exists():
        raise ValueError(
            "You are trying to specify the path to a session sub-directory. "
            "Specify the main simulation directory instead and "
            "the session_id (optional)."
        )

    Simul = import_cls_simul(short_name)

    # Load parameters
    from snek5000.params import load_params

    params = load_params(path_dir)

    # Modify parameters prior to loading
    params.NEW_DIR_RESULTS = False
    params.output.HAS_TO_SAVE = False
    params.path_run = path_dir

    if isinstance(session_id, int):
        from snek5000.output import _make_path_session

        params.output.session_id = session_id
        params.output.path_session = _make_path_session(path_dir, session_id)

    sim = Simul(params)
    return sim


# for consistency with fluidsim
load = load_simul  #: Alias for :func:`load_simul`


from .util.smake import append_debug_flags, ensure_env  # noqa: F401, E402
from .util import restart  # noqa: F401, E402

get_status = restart.get_status  #: Alias for :func:`snek5000.util.restart.get_status`
load_for_restart = (
    restart.load_for_restart
)  #: Alias for :func:`snek5000.util.restart.load_for_restart`
