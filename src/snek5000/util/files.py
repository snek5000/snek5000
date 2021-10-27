import re
from pathlib import Path

from .. import logger


def next_path(old_path, force_suffix=False):
    """Generate a new path with an integer suffix

    Parameters
    ----------
    old_path: str or path-like
        Path to check for existence

    force_suffix:
        If true, will not check if the `old_path` can be used and adds
        a suffix in the end.

    Returns
    -------
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
        logger.debug(f"Checking if path exists: {new_path}")
        new_path = int_suffix(old_path, i)
        i += 1

    logger.debug(f"Next path available: {new_path}")

    return new_path
