"""Utilities to restart a simulation
====================================

"""
import os
from enum import Enum
from pathlib import Path
from warnings import warn

from fluiddyn.io import FLUIDSIM_PATH

from ..log import logger
from ..output import _make_path_session
from ..params import load_params
from ..solvers import get_solver_short_name, import_cls_simul
from .files import next_path


class SnekRestartError(Exception):
    pass


class SimStatus(Enum):
    """Simulation status inspired from HTTP response status codes_.

    .. _codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

    """

    OK = (200, "OK: All prerequisities satisfied to restart.")
    RESET_CONTENT = (
        205,
        (
            "Reset Content: Multi-file restart found. Some field files exist. "
            "Restarting in the same session would overwrite files. "
            "Ensure current session is archived or restart in a new session."
        ),
    )
    PARTIAL_CONTENT = (
        206,
        (
            "Partial Content: No multi-file restart found. Some field files exist."
            "Ensure current session is archived or restart in a new session."
        ),
    )
    NOT_FOUND = (
        404,
        "Not Found: SIZE and/or nek5000 and/or SESSION.NAME files are missing.",
    )
    LOCKED = (
        423,
        (
            "Locked: The path is currently locked by snakemake. "
            "Execute `snakemake --unlock` or see prepare_for_restart function."
        ),
    )
    TOO_EARLY = (
        425,
        "Too Early: Seems like snakemake was never executed.",
    )

    def __init__(self, code: int, message: str):
        self.code = code  #: status code
        self.message = message  #: helpful description


def get_status(path_dir, session_id=None, verbose=False):
    """Get status of a simulation run by verifying its contents. It checks if:

    - snakemake was ever executed
    - directory is locked by snakemake (either due to a running
      simulation or a terminated one)
    - necessary files for starting a simulation exist
    - restart files exist

    Parameters
    ----------
    path : str or path-like
        Path to an existing simulation directory
    session_id : int
        Integer suffix of the session directory
    verbose : bool
        Print out the path and its contents

    Returns
    -------
    _ : SimStatus
        Enumeration indicating status code and message

    """
    path = Path(path_dir)
    if session_id:
        path_session = _make_path_session(path, session_id)
    else:
        path_session = Path(load_params(path_dir).output.path_session)

    locks_dir = path / ".snakemake" / "locks"
    contents = os.listdir(path)

    if verbose:
        print(path, "\nContents:", contents)

    if not (path / ".snakemake").exists():
        return SimStatus.TOO_EARLY
    elif locks_dir.exists():
        locks = tuple(locks_dir.iterdir())
        if locks:
            return SimStatus.LOCKED

    if not {"SIZE", "SESSION.NAME", "nek5000"}.issubset(contents):
        return SimStatus.NOT_FOUND

    checkpoints = set(path_session.glob("rs6*0.f?????"))
    field_files = set(path_session.glob("*0.f?????")) - checkpoints

    if checkpoints and field_files:
        return SimStatus.RESET_CONTENT
    elif field_files:
        return SimStatus.PARTIAL_CONTENT
    else:
        return SimStatus.OK


def prepare_for_restart(path, chkp_fnumber=1, verify_contents=True):
    """Load only params for a restart. Use :func:`load_for_restart()` instead.

    .. deprecated: 0.8.0b0

    """
    warn(
        (
            "Function prepare_for_restart is deprecated."
            "Kept for compatibility and would disappear in version 0.9.0b0"
        ),
        DeprecationWarning,
    )
    params, _ = load_for_restart(
        path, use_checkpoint=chkp_fnumber, verify_contents=verify_contents
    )
    return params


def load_for_restart(
    path_dir=".", use_start_from=None, use_checkpoint=None, verify_contents=True
):
    """Load params and Simul for a restart.

    >>> params, Simul = load_for_restart(name_dir)

    Parameters
    ----------

    path_dir: str or path-like (optional)
        The directory of an existing simulation. If nothing is given, we load the
        data in the current directory.  Can be an absolute path, a relative path,
        or even simply just the name of the directory under $FLUIDSIM_PATH.

    use_start_from: str
        Name of the field file to restart from. Mutually exclusive option with
        ``use_checkpoint``.

    use_checkpoint: int, {1, 2}
        Number of the multi-file checkpoint file set to restart from. Mutually
        exclusive parameter with ``use_start_from``.

    verify_contents: bool
        Verify directory contents to avoid runtime errors.

    Notes
    -----
    How it works:

    - If ``verify contents`` is `True`, do so using :func:`get_status`
    - Reads ``params_simul.xml`` if it exists, and if not falls back to ``.par`` file.
    - Modifies parameters (in memory, but does not write into the filesystem,
      yet) ``start_from`` (Nek5000) or checkpoint module (requires KTH
      framework) with appropriate ``chkp_fnumber`` to restart from.

    """
    path = Path(path_dir)

    if not path.exists():
        logger.info("Trying to open the path relative to $FLUIDSIM_PATH")
        path = Path(FLUIDSIM_PATH) / path_dir

    try:
        params = load_params(path)
    except (ValueError, OSError) as err:
        raise SnekRestartError(err)

    status = get_status(path, params.output.session_id)

    if verify_contents:
        if status.code >= 400:
            raise SnekRestartError(f"{status.code}: {status.message}")
        else:
            logger.info(f"{status.code}: {status.message}")

    # Load Simul class and parameters
    short_name = get_solver_short_name(path)

    try:
        Simul = import_cls_simul(short_name)
    except ImportError:
        raise ImportError(f"Cannot import Simul class of solver {short_name}")

    # Set restart file
    if use_start_from and use_checkpoint:
        raise SnekRestartError(
            "Options use_start_from and use_checkpoint are mutually exclusive. "
            "Use only one option at a time."
        )
    else:
        old_path_session = Path(params.output.path_session)
        session_id, new_path_session = next_path(
            path / "session", force_suffix=True, return_suffix=True
        )
        params.output.session_id = session_id
        params.output.path_session = new_path_session

        new_path_session.mkdir()

    def make_relative_symlink(file_name):
        src = new_path_session / file_name
        dest = f"../{old_path_session.name}/{file_name}"
        logger.debug(f"Symlinking {src} -> {dest}")
        src.symlink_to(dest)

    if use_start_from:
        if (old_path_session / use_start_from).exists():
            params.nek.general.start_from = use_start_from
            make_relative_symlink(use_start_from)
        else:
            raise SnekRestartError(f"Restart file {use_start_from} not found")
    elif use_checkpoint:
        if use_checkpoint in (1, 2) and status in (
            SimStatus.OK,
            SimStatus.RESET_CONTENT,
        ):
            params.nek.chkpoint.chkp_fnumber = use_checkpoint
            params.nek.chkpoint.read_chkpt = True

            for restart_file in old_path_session.glob(f"rs6{short_name}0.f?????"):
                make_relative_symlink(restart_file.name)
        else:
            raise SnekRestartError(
                f"Restart checkpoint {use_checkpoint} is invalid / does not exist"
            )
    else:
        logger.info(
            "No restart files were requested. "
            "This would result in a fresh simulation in a new session."
        )

    if hasattr(params, "output") and hasattr(params.output, "HAS_TO_SAVE"):
        params.output.HAS_TO_SAVE = True

    params.NEW_DIR_RESULTS = False

    return params, Simul
