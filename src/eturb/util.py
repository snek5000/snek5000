"""Miscellaneous utilities
==========================


"""
import os
import sys
from pathlib import Path
from datetime import datetime
from functools import reduce
from tarfile import TarFile
from zipfile import ZipFile

from fluiddyn import util
from .params import Parameters
from .log import logger


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
    """Setup environment variables in preparation for Nek5000 build."""
    here = Path(__file__).parent
    if not os.getenv("SOURCE_ROOT"):
        os.environ["SOURCE_ROOT"] = source_root = str(
            (here / "../../../lib/Nek5000").absolute()
        )

    env_path = str(os.getenv("PATH"))
    if source_root not in env_path:
        os.environ["PATH"] = path = ":".join((source_root, env_path))

    return source_root, path


def init_params(Class, isolated_unit=False):
    """Instantiate an isolated ``params`` for a specific class."""
    if hasattr(Class, "create_default_params") and not isolated_unit:
        params = Class.create_default_params()
    else:
        from .params import Parameters

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
                line.startswith(underline)
                for underline in ("====", "----", "~~~~")
            ):
                continue
            else:
                lines.append(indent + line)

            prev_line = line

        doc = "\n".join((lines))

    return doc


def prepare_for_restart(path, chkp_fnumber=1, verify_contents=True):
    contents = os.listdir(path)
    path = Path(path)

    if verify_contents:
        locks_dir = path / ".snakemake" / "locks"
        if not locks_dir.exists():
            raise IOError(f"Seems like snakemake was never executed: {path}")
        else:
            locks = tuple(locks_dir.iterdir())
            if locks:
                raise IOError(
                    f"The path is currently locked by snakemake: {path}"
                )

        if not {"SIZE", "SESSION.NAME", "nek5000"}.issubset(contents):
            raise IOError(
                f"SIZE and/or nek5000 and/or SESSION.NAME files are missing: {path}"
            )
        if not tuple(path.glob("rs6*")):
            raise IOError(f"No restart files found: {path}")

    if "params.xml" in contents:
        params = Parameters(tag="params", path_file=(path / "params.xml"))
    else:
        # FIXME: make this generic for all possible solvers
        # Trying to read the par file
        assert path.name.startswith("abl")
        logger.warning("No params.xml found... Attempting to read abl.par")

        from eturb.solvers.abl import Simul

        params = Simul.create_default_params()
        params.nek._read_par(path / "abl.par")

    params.nek.chkpoint.chkp_fnumber = chkp_fnumber
    params.nek.chkpoint.read_chkpt = True

    return params
