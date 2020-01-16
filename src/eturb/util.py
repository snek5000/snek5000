import os
from zipfile import ZipFile
from tarfile import TarFile
from datetime import datetime
from fluiddyn import util


def timestamp(path):
    """Modification date of a file or directory as a timestamp.

    Returns
    -------
    str

      In the modified ISO format YYYY-MM-DDTHH-MM-SS

    """
    return (
        util.modification_date(path)
        .isoformat(timespec="seconds")
        .replace(":", "-")
    )


# Functions used in rules
def isoformat(dt):
    return dt.isoformat(timespec="seconds").replace(":", "-")


def modification_date(path):
    """Modification date of a file or directory"""
    if os.path.exists(path):
        t = os.path.getmtime(path)
        return isoformat(datetime.fromtimestamp(t))
    else:
        return ""


def now():
    return isoformat(datetime.now())


def zip_info(filename):
    with ZipFile(filename) as file:
        # Print all contents
        file.printdir()


def tar_info(filename):
    with TarFile(filename) as file:
        # Print all contents
        file.list()
