"""Miscellaneous utilities
==========================

.. autosummary::
   :toctree:

   archive
   smake

"""
import os
import sys
from datetime import datetime
from functools import reduce
from pathlib import Path
from tarfile import TarFile
from zipfile import ZipFile

from fluiddyn import util

from .. import source_root
from ..log import logger


def isoformat(dt):
    """Returns timestamp in modified isoformat from a datetime object (-
    instead of :). Accurate upto seconds.

    .. note:: The modified ISO format is YYYY-MM-DDTHH-MM-SS

    """
    return dt.isoformat(timespec="seconds").replace(":", "-")


def timestamp(path):
    """Modification date of a file or directory as a timestamp.

    :returns str:

    """
    return isoformat(util.modification_date(path))


def modification_date(path):
    """Modification date of a file or directory. Returns empty string if does
    not exist.

    """
    if os.path.exists(path):
        t = os.path.getmtime(path)
        return isoformat(datetime.fromtimestamp(t))
    else:
        return ""


def now():
    """The current timestamp.

    :returns str:

    """
    return isoformat(datetime.now())


def zip_info(filename):
    """Contents of a zip file."""
    with ZipFile(filename) as file:
        # Print all contents
        file.printdir()


def tar_info(filename):
    """Contents of a tar file."""
    with TarFile(filename) as file:
        # Print all contents
        file.list()


def scantree(path):
    """Recursively yield DirEntry objects for given directory.

    Courtesy: https://stackoverflow.com/a/33135143

    :returns generator: A generator for ``DirEntry`` objects.

    """
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def last_modified(path):
    """Find the last modified file in a directory tree.

    :returns DirEntry:

    """
    return reduce(
        lambda x, y: x if x.stat().st_mtime > y.stat().st_mtime else y,
        scantree(path),
    )


def activate_paths():
    """Setup environment variables in preparation for Nek5000 build.

    .. deprecated:: 0.6.0
       Use :func:`snek5000.source_root`
       and :func:`snek5000.util.smake.ensure_env` instead.

    """
    import warnings

    warnings.warn(
        (
            "Function activate_paths will be removed on a later release. Use "
            "source_root and ensure_env instead"
        ),
        DeprecationWarning,
    )

    env_source_root = os.environ["NEK_SOURCE_ROOT"] = source_root()

    env_path = str(os.getenv("PATH"))
    if env_source_root not in env_path:
        os.environ["PATH"] = ":".join((env_source_root + "/bin", env_path))

    return env_source_root, env_path


def init_params(Class, isolated_unit=False):
    """Instantiate an isolated ``params`` for a specific class."""
    if hasattr(Class, "create_default_params") and not isolated_unit:
        params = Class.create_default_params()
    else:
        from ..params import Parameters

        params = Parameters(tag="params")
        Class._complete_params_with_default(params)

    return params


def docstring_params(Class, sections=False, indent_len=4):
    """Creates a parameter instance and generate formatted docs for it. The
    docs are defined by the ``params.<child>._set_doc`` method. Done only when
    ``sphinx`` is already imported.

    """
    if "sphinx" in sys.modules:
        params = init_params(Class, isolated_unit=True)
        doc = params._get_formatted_docs()
    else:
        doc = ""

    if not sections:
        lines = []
        indent = " " * indent_len
        prev_line = ""

        for line in doc.splitlines():
            if line.startswith("Documentation for"):
                lines.append(f"{indent}**{line.lstrip()}**")
            elif "Documentation for" in prev_line and any(
                line.startswith(underline) for underline in ("====", "----", "~~~~")
            ):
                continue
            else:
                lines.append(indent + line)

            prev_line = line

        doc = "\n".join((lines))

    return doc


def get_status(path):
    """Get status of a simulation run by verifying its contents.

    :returns tuple(int, str): status code and message

    """
    locks_dir = path / ".snakemake" / "locks"
    contents = os.listdir(path)

    if not (path / ".snakemake").exists():
        return (
            425,
            f"Too Early: Seems like snakemake was never executed: {path}",
        )
    elif locks_dir.exists():
        locks = tuple(locks_dir.iterdir())
        if locks:
            return (
                423,
                f"Locked: The path is currently locked by snakemake: {path}",
            )

    if not {"SIZE", "SESSION.NAME", "nek5000"}.issubset(contents):
        return (
            404,
            (
                "Not Found: SIZE and/or nek5000 and/or SESSION.NAME files are missing: "
                f"{path}: Contents: {contents}"
            ),
        )
    if not tuple(path.glob("rs6*")):
        return (404, f"Not Found: No restart files found: {path}")

    return (200, f"OK: All prerequisities satisfied to restart: {path}")


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
        status, msg = get_status(path)
        if status >= 400:
            logger.error(f"{status}: {msg}")
        else:
            logger.info(f"{status}: {msg}")

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
