import re
from pathlib import Path
from shutil import copy2

from .. import logger
from ..params import load_params


def next_path(old_path, force_suffix=False, return_suffix=False):
    """Generate a new path with an integer suffix

    Parameters
    ----------
    old_path: str or path-like
        Path to check for existence

    force_suffix:
        If true, will not check if the `old_path` can be used and adds
        a suffix in the end.

    return_suffix:
        If true, returns the integer suffix along with the path/

    Returns
    -------
    (i, new_path): tuple[int, Path]
        If `return_suffix` is `True`.

    new_path: Path
        A path (with an integer suffix) which does not yet exist in the
        filesystem.

    Example
    -------
    >>> import os
    >>> os.chdir("/tmp")

    >>> next_path("test.txt")  # path does not exist
    PosixPath('test.txt')

    >>> next_path("test.txt", force_suffix=True)  # path does not exists
    PosixPath('test_00.txt')

    >>> Path("test.txt").touch()
    >>> next_path("test.txt")  # path exists
    PosixPath('test_00.txt')

    >>> Path("test_00.txt").touch()
    >>> next_path("test.txt")  # path and the next one both exists
    PosixPath('test_01.txt')

    >>> Path("test.txt").unlink()  # cleanup
    >>> Path("test_00.txt").unlink()

    """

    def int_suffix(p, integer):
        stem = p.stem
        # for example: remove .tar from the end, if any
        for suffix in p.suffixes:
            stem = re.sub(f"{suffix}$", "", stem)

        return p.parent / "".join([stem, f"_{integer:02d}", *p.suffixes])

    old_path = Path(old_path)

    if not force_suffix and not old_path.exists():
        return old_path

    i = 0
    new_path = int_suffix(old_path, i)

    while new_path.exists():
        logger.debug(f"Path exists: {new_path}")
        i += 1
        new_path = int_suffix(old_path, i)

    logger.debug(f"Next path available: {new_path}")

    return (i, new_path) if return_suffix else new_path


def create_session(case, re2, ma2, par):
    """Creates a session and write the path to a `SESSION.NAME` file.
    Then, symlinks re2 and ma2 files, and copies the par file.

    Parameters
    ----------
    case : str
        Case name
    re2 : str
        Mesh file name
    ma2 : str
        Connectivity mapping file name
    par : str
        Parameter file name

    """
    params = load_params()
    session_dir = Path(params.output.path_session).relative_to(params.path_run)

    session_dir.mkdir(exist_ok=True)

    with open("SESSION.NAME", "w") as session_name:
        # use relative paths to avoid 132 character limit in Nek5000
        session_name.write(f"{case}\n./{session_dir}\n")

    for file in (re2, ma2):
        # use relative symlinks
        (session_dir / file).symlink_to(f"../{file}")

    # Copy par files to run without recompiling
    copy2(par, session_dir / par)
