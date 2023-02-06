# isort: skip_file
"""
API reference

.. rubric:: Sub-packages

.. autosummary::
   :toctree:

   resources
   output
   solvers
   util

.. rubric:: Modules

.. autosummary::
   :toctree:

   clusters
   const
   info
   log
   magic
   make
   operators
   params
   config

"""

from importlib import resources as _resources
import os
import weakref
from pathlib import Path

from fluiddyn.util import mpi  # noqa: F401

from ._version import __version__  # noqa: F401
from .log import logger  # noqa: F401
from .params import load_params


def get_nek_source_root():
    """Path of Nek5000 source code."""
    if os.getenv("SOURCE_ROOT"):
        logger.warning(
            "The environment variable "
            "SOURCE_ROOT is deprecated in v19, use NEK_SOURCE_ROOT instead."
        )

    try:
        NEK_SOURCE_ROOT = os.environ["NEK_SOURCE_ROOT"]
    except KeyError:
        raise RuntimeError(
            "NEK_SOURCE_ROOT has to point to Nek5000 top level directory."
        )

    nek5000 = str(Path(os.path.expandvars(NEK_SOURCE_ROOT)).expanduser().absolute())

    if not os.path.exists(nek5000):
        logger.error("NEK_SOURCE_ROOT: " + nek5000)
        raise IOError(
            "Cannot find Nek5000 source code. Use environment variable "
            "NEK_SOURCE_ROOT to point to Nek5000 top level directory."
        )
    return nek5000


def get_snek_resource(resource_name):
    """Fetches path of a file from subpackage ``snek5000.resources``.

    Parameters
    ----------
    resource_name: str

        Name of a file packaged in :mod:`snek5000.resources`

    """
    try:
        path = next(_resources.path("snek5000.resources", resource_name).gen)
    except AttributeError:
        path = _resources.path("snek5000.resources", resource_name)
    return path


def load_simul(path_dir=".", session_id=None, reader=True):
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

    reader: bool or str
        By default (`reader=True`) invokes
        :meth:`sim.output.phys_fields.init_reader()
        <snek5000.output.phys_fields.PhysFields.init_reader>`. If a string is
        provided, it is passed onto
        :meth:`sim.output.phys_fields.change_reader(reader)
        <snek5000.output.phys_fields.PhysFields.change_reader>`.


    .. hint::

        An common use case of ``session_id`` parameter is to load field
        files from old sessions using the :meth:`sim.output.get_field_file
        <snek5000.output.base.Output.get_field_file>` method

    """
    from snek5000.util.files import _path_try_from_fluidsim_path

    path_dir = _path_try_from_fluidsim_path(path_dir)

    # Load simulation class
    from snek5000.solvers import import_cls_simul, get_solver_short_name
    from snek5000.output import _parse_path_run_session_id

    # In case the user specifies the path to a session sub-directory
    if session_id is None:
        path_dir, session_id = _parse_path_run_session_id(path_dir)

    short_name = get_solver_short_name(path_dir)
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

    if reader:
        if reader is True:
            sim.output.phys_fields.init_reader()
        elif isinstance(reader, str):
            sim.output.phys_fields.change_reader(reader)
        else:
            raise ValueError(
                f"Reader should be either True or False or one of {params.output.phys_fields.available_readers = }"
            )

    return sim


# for consistency with fluidsim
load = weakref.proxy(load_simul)  #: Alias for :func:`load_simul`


from .util.smake import append_debug_flags, ensure_env  # noqa: F401, E402
from .util import restart  # noqa: F401, E402

get_status = restart.get_status  #: Alias for :func:`snek5000.util.restart.get_status`
load_for_restart = (
    restart.load_for_restart
)  #: Alias for :func:`snek5000.util.restart.load_for_restart`


__all__ = [
    "get_nek_source_root",
    "get_snek_resource",
    "get_status",
    "load",
    "load_for_restart",
    "load_params",
    "load_simul",
    "logger",
]
