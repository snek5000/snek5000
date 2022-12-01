"""List files with no extensions"""
import os
from pathlib import Path

try:
    NEK_SOURCE_ROOT = Path(os.environ["NEK_SOURCE_ROOT"])
except KeyError:
    raise RuntimeError("NEK_SOURCE_ROOT has to be defined")


def is_upper(name):
    return name.upper() == name


def ls_no_ext(root, suffix="", prefix=""):
    files = Path(root).glob("*")
    for file in files:
        if not file.suffix and is_upper(file.name):
            print("{}{}{}".format(suffix, file.name, prefix))


if __name__ == "__main__":
    # For doxygen
    ls_no_ext(NEK_SOURCE_ROOT / "core", " " * 25, " \\")
    ls_no_ext("../src/abl/toolbox", " " * 25, " \\")

    # For vim
    # ls_no_ext(NEK_SOURCE_ROOT / "core", " "*12 + "\\ ", ",")
