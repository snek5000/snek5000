"""Utilities to restart a simulation
====================================

"""
import os
from enum import Enum
from pathlib import Path
from warnings import warn

from fluiddyn.io import FLUIDSIM_PATH

from ..log import logger
from ..solvers import get_solver_short_name, import_cls_simul


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


def get_status(path, verbose=False):
    """Get status of a simulation run by verifying its contents. It checks if:

    - snakemake was ever executed
    - directory is locked by snakemake (either due to a running
      simulation or a terminated one)
    - necessary files for starting a simulation exist
    - restart files exist

    Parameters
    ----------
    path : str
        Path to an existing simulation directory
    verbose : bool
        Print out the path and its contents

    Returns
    -------
    _ : SimStatus
        Enumeration indicating status code and message

    """
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

    checkpoints = set(path.glob("rs6*0.f?????"))
    field_files = set(path.glob("*0.f?????")) - checkpoints

    if checkpoints and field_files:
        return SimStatus.RESET_CONTENT
    elif field_files:
        return SimStatus.PARTIAL_CONTENT
    else:
        return SimStatus.OK


def prepare_for_restart(path, chkp_fnumber=1, verify_contents=True):
    """Use :func:`load_for_restart()` instead.

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

    .. todo::

        Possibility to make a new session


    Notes
    -----
    How it works:

    - If ``verify contents`` is `True`, do so using :func:`get_status`
    - Reads ``params_simul.xml`` if it exists, and if not falls back to ``.par`` file.
    - Modifies ``start_from`` (Nek5000) or checkpoint module (requires KTH
      framework) parameters with appropriate ``chkp_fnumber`` to restart from.

    """
    contents = os.listdir(path_dir)
    path = Path(path_dir)
    if not path.exists():
        logger.info("Trying to open the path relative to $FLUIDSIM_PATH")
        path = Path(FLUIDSIM_PATH) / path_dir

    status = get_status(path)

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

    if "params_simul.xml" in contents:
        params = Simul.load_params_from_file(path_xml=str(path / "params_simul.xml"))
    else:
        # Trying to read the par file
        logger.warning(
            f"No params_simul.xml found... Attempting to read {short_name}.par"
        )

        params = Simul.create_default_params()
        params.nek._read_par(path / f"{short_name}.par")

    # Set restart file
    if use_start_from and use_checkpoint:
        raise SnekRestartError(
            "Options use_start_from and use_checkpoint are mutually exclusive. "
            "Use only one option at a time."
        )
    elif use_start_from:
        if (path / use_start_from).exists():
            params.nek.general.start_from = use_start_from
        else:
            raise SnekRestartError(f"Restart file {use_start_from} not found")
    elif use_checkpoint:
        if use_checkpoint in (1, 2) and status in (
            SimStatus.OK,
            SimStatus.RESET_CONTENT,
        ):
            params.nek.chkpoint.chkp_fnumber = use_checkpoint
            params.nek.chkpoint.read_chkpt = True
        else:
            raise SnekRestartError(
                f"Restart checkpoint {use_checkpoint} is invalid / does not exist"
            )

    params.nek._write_par(path / f"{short_name}.par")
    params.NEW_DIR_RESULTS = False

    return params, Simul
