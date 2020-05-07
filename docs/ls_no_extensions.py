"""List files with no extensions"""
from pathlib import Path


def is_upper(name):
    return name.upper() == name


def ls_no_ext(root, suffix="", prefix=""):
    files = Path(root).glob("*")
    for file in files:
        if not file.suffix and is_upper(file.name):
            print("{}{}{}".format(suffix, file.name, prefix))


if __name__ == "__main__":
    # For doxygen
    ls_no_ext("../lib/Nek5000/core", " " * 25, " \\")
    ls_no_ext("../src/abl/toolbox", " " * 25, " \\")

    # For vim
    # ls_no_ext("../lib/Nek5000/core", " "*12 + "\\ ", ",")
