"""Miscellaneous utilities
==========================

.. autosummary::
   :toctree:

   archive
   console
   files
   restart
   smake

"""
import itertools
import os
import sys
from datetime import datetime
from functools import partial, reduce
from tarfile import TarFile
from zipfile import ZipFile

from fluiddyn import util

from .. import get_nek_source_root
from .restart import get_status

__all__ = ["get_nek_source_root", "get_status"]

repeat = partial(itertools.repeat, None)
repeat.__doc__ = """\
Iterator which returns a ``None`` object for a number of times.

.. note::

        Using :func:`itertools.repeat` instead of :func:`range` is considered a
        more efficient option when the iterated value is unused.
        https://stackoverflow.com/a/9098860


Examples
--------
>>> for _ in repeat(10):
...     # do something


"""


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
    doc = doc.replace("Documentation for params\n========================", "")

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
