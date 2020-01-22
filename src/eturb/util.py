"""Miscellaneous utilities
==========================


"""
import os
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from functools import reduce
from tarfile import TarFile
from zipfile import ZipFile

from fluiddyn import util


def isoformat(dt):
    """Returns timestamp in modified isoformat from a datetime object (-
    instead of :). Accurate upto seconds.

    Note
    ----
    The modified ISO format is YYYY-MM-DDTHH-MM-SS

    """
    return dt.isoformat(timespec="seconds").replace(":", "-")


def timestamp(path):
    """Modification date of a file or directory as a timestamp.

    Returns
    -------
    str

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
    """Return current timestamp."""
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

    Yields
    ------
    A generator for ``DirEntry`` objects.

    """
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)
        else:
            yield entry


def last_modified(path):
    """Find the last modified file in a directory tree.

    Returns
    -------
    A ``DirEntry`` object.

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


@contextmanager
def change_dir(path_dir):
    """Context manager to temporarily change to another directory."""
    try:
        curdir = Path.cwd()
        os.chdir(path_dir)
        yield
    finally:
        os.chdir(curdir)
