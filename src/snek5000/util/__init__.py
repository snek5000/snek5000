"""Miscellaneous utilities
==========================

.. autosummary::
   :toctree:

   archive
   files
   restart
   smake

"""
import os
import re
import sys
from datetime import datetime
from functools import reduce
from tarfile import TarFile
from zipfile import ZipFile

from fluiddyn import util

from .. import source_root
from .restart import (  # noqa: kept for backwards compatibility
    get_status,
    prepare_for_restart,
)


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
        try:
            Class._complete_params_with_default(params)
        except TypeError:
            from snek5000.info import InfoSolverMake

            info_solver = InfoSolverMake()

            Class._complete_params_with_default(params, info_solver)

    return params


def docstring_params(Class, sections=False, indent_len=4):
    """Creates a parameter instance and generate formatted docs for it. The
    docs are defined by the ``params.<child>._set_doc`` method. Done only when
    ``sphinx`` is already imported.

    """
    if "sphinx" in sys.modules:
        params = init_params(Class, isolated_unit=True)
        doc = "\n" + params._get_formatted_docs()
    else:
        doc = ""

    # Remove the first heading: typically no content
    doc = re.sub(r"^\s+Documentation\ for\ params$", "", doc, flags=re.MULTILINE)

    if not sections:
        lines = []
        indent = " " * indent_len
        prev_line = ""

        for line in doc.splitlines():
            if line.startswith("Documentation for"):
                heading = line.lstrip()
                idx = heading.index(" for ") + 5
                # Add target for cross referencing
                lines.append(f"{indent}.. _{heading[idx:]}:\n")
                lines.append(f"{indent}**{heading}**")
            elif "Documentation for" in prev_line and any(
                line.startswith(underline) for underline in ("====", "----", "~~~~")
            ):
                continue
            else:
                lines.append(indent + line)

            prev_line = line

        doc = "\n".join((lines))

    return doc
