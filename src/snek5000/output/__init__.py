"""
Manage outputs

.. autosummary::
   :toctree:

   base
   history_points
   print_stdout
   phys_fields
   spatial_means
   remaining_clock_time

"""
from pathlib import Path


def _make_path_session(path_run: str, session_id: int):
    """Create a path object pointing to session directory.

    Parameters
    ----------
    path_run : str
    session_id : int
    """
    return Path(path_run) / f"session_{session_id:02d}"


def _parse_path_run_session_id(path_session):
    """Parse `path_run` and `session_id` from path_session

    Parameters
    ----------
    path_session : str

    Returns
    -------
    path_dir, session_id: tuple[Path, int | None]
        If the path is to a session_directory the `path_run` (its parent path)
        and the `session_id` will be returned. If not the input parameter will
        be returned as a path object unchanged, along with `None` instead
        of `session_id`.

    """
    path_session = Path(path_session).resolve()

    head, underscore, tail = path_session.name.partition("_")
    if head == "session" and underscore == "_" and tail.isdecimal():
        return path_session.parent, int(tail)
    else:
        return path_session, None
