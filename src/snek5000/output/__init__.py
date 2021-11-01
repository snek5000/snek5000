"""
Manage outputs

.. autosummary::
   :toctree:

   base
   print_stdout
   phys_fields


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
