"""Utilities to restart a simulation
====================================

"""
import os
from enum import Enum
from pathlib import Path

from ..log import logger


class SimStatus(Enum):
    """Simulation status inspired from HTTP response status codes_.

    .. _codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

    """

    OK = (200, "OK: All prerequisities satisfied to restart")
    NOT_FOUND = (
        404,
        "Not Found: SIZE and/or nek5000 and/or SESSION.NAME files are missing.",
    )
    EXPECTATION_FAILED = (417, "Expectation Failed: No restart files found")
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
    """Get status of a simulation run by verifying its contents.

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

    if not tuple(path.glob("rs6*")):
        return SimStatus.EXPECTATION_FAILED

    return SimStatus.OK


def prepare_for_restart(path, chkp_fnumber=1, verify_contents=True):
    """Takes a directory in which a simulation was executed.

    * If verify contents:
      - check if snakemake was ever executed or check if directory is locked by snakemake
      - ensures simulation files exist
      - ensures restart files exist
    * Reads params_simul.xml if it exists, and if not falls back to .par file.
    * Modifies checkpoint parameters with appropriate ``chkp_fnumber`` to
      restart from KTH framework.

    """
    contents = os.listdir(path)
    path = Path(path)

    if verify_contents:
        status = get_status(path)
        if status.code >= 400:
            logger.error(f"{status.code}: {status.message}")
        else:
            logger.info(f"{status.code}: {status.message}")

    # FIXME: make this generic for all possible solvers
    # Trying to read the par file
    solver_prefix = path.absolute().name.split("_")[0]
    try:
        from importlib import import_module

        Simul = import_module(f"{solver_prefix}.solver").Simul
    except ImportError:
        raise ImportError("Cannot import simulation class")

    if "params_simul.xml" in contents:
        params = Simul.load_params_from_file(path_xml=str(path / "params_simul.xml"))
    else:
        logger.warning(
            f"No params_simul.xml found... Attempting to read {solver_prefix}.par"
        )

        params = Simul.create_default_params()
        params.nek._read_par(path / f"{solver_prefix}.par")

    params.nek.chkpoint.chkp_fnumber = chkp_fnumber
    params.nek.chkpoint.read_chkpt = True

    return params
