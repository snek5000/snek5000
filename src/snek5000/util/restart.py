"""Utilities to restart a simulation
====================================

"""
import os
import sys
from enum import Enum
from pathlib import Path
from textwrap import dedent

from fluidsim_core.scripts.restart import RestarterABC

from ..log import logger
from ..output import _make_path_session, _parse_path_run_session_id
from ..params import load_params
from ..solvers import get_solver_short_name, import_cls_simul
from .files import _path_try_from_fluidsim_path, next_path


class SnekRestartError(Exception):
    pass


class SimStatus(Enum):
    """Simulation status inspired from HTTP response status codes_.

    .. _codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

    """

    OK = (200, "OK: All prerequisities satisfied to restart.")
    RESET_CONTENT = (
        205,
        (
            "Reset Content: Multi-file restart found. Some field files exist. "
            "Restarting in the same session would overwrite files. "
            "Ensure current session is archived or restart in a new session or "
            "a new directory."
        ),
    )
    PARTIAL_CONTENT = (
        206,
        (
            "Partial Content: No multi-file restart found. Some field files exist. "
            "Ensure current session is archived or restart in a new session or "
            "a new directory."
        ),
    )
    NOT_FOUND = (
        404,
        "Not Found: SIZE and/or nek5000 is missing.",
    )
    LOCKED = (
        423,
        (
            "Locked: The path is currently locked by snakemake. "
            "Execute `snakemake --unlock` function snek5000.make.unlock."
        ),
    )
    TOO_EARLY = (
        425,
        "Too Early: Seems like snakemake was never executed.",
    )

    def __init__(self, code: int, message: str):
        self.code = code  #: status code
        self.message = message  #: helpful description


def get_status(path_dir, session_id=None, verbose=False):
    """Get status of a simulation run by verifying its contents. It checks if:

    - snakemake was ever executed
    - directory is locked by snakemake (either due to a running
      simulation or a terminated one)
    - necessary files for starting a simulation exist
    - restart files exist

    Parameters
    ----------
    path : str or path-like
        Path to an existing simulation directory
    session_id : int
        Integer suffix of the session directory
    verbose : bool
        Print out the path and its contents

    Returns
    -------
    _ : SimStatus
        Enumeration indicating status code and message

    """
    path = Path(path_dir)
    if session_id:
        path_session = _make_path_session(path, session_id)
    else:
        path_session = Path(load_params(path_dir).output.path_session)

    locks_dir = path / ".snakemake" / "locks"
    contents = os.listdir(path)

    if verbose:
        print(path, "\nContents:", contents)

    if not (path / ".snakemake").exists():
        return SimStatus.TOO_EARLY
    elif locks_dir.exists():
        locks = tuple(locks_dir.iterdir())
        if locks:
            return SimStatus.LOCKED

    if not {"SIZE", "nek5000"}.issubset(contents):
        return SimStatus.NOT_FOUND

    checkpoints = set(path.glob("rs6*0.f?????"))
    field_files = set(path_session.glob("*0.f?????"))

    if checkpoints and field_files:
        return SimStatus.RESET_CONTENT
    elif field_files:
        return SimStatus.PARTIAL_CONTENT
    else:
        return SimStatus.OK


def load_for_restart(
    path_dir=".",
    use_start_from=None,
    use_checkpoint=None,
    session_id=None,
    verify_contents=True,
    new_dir_results=False,
    only_check=False,
):
    """Load params and Simul for a restart.

    >>> params, Simul = load_for_restart(name_dir)

    Parameters
    ----------

    path_dir: str or path-like (optional)
        The directory of an existing simulation. If nothing is given, we load the
        data in the current directory.  Can be an absolute path, a relative path,
        or even simply just the name of the directory under $FLUIDSIM_PATH.

    use_start_from: str or int
        Name or index of the field file to restart from. Mutually exclusive option
        with ``use_checkpoint``.

    use_checkpoint: int, {1, 2}
        Number of the multi-file checkpoint file set to restart from. Mutually
        exclusive parameter with ``use_start_from``.

    session_id: int
        Indicate which session directory should be used to look for restart files.
        If not specified it would default to the `path_session` value last
        recorded in the `params_simul.xml` file.

    verify_contents: bool
        Verify directory contents to avoid runtime errors.

    new_dir_results: bool (default False)
        Create a new directory for the new simulation.

    Notes
    -----
    How it works:

    - If ``verify contents`` is `True`, do so using :func:`get_status`
    - Reads ``params_simul.xml`` if it exists, and if not falls back to ``.par`` file.
    - Modifies parameters (in memory, but does not write into the filesystem,
      yet) ``start_from`` (Nek5000) or checkpoint module (requires KTH
      framework) with appropriate ``chkp_fnumber`` to restart from.

    """
    path = _path_try_from_fluidsim_path(path_dir)

    # In case the user specifies the path to a session sub-directory
    if session_id is None:
        path, session_id = _parse_path_run_session_id(path)

    try:
        params = load_params(path)
    except (ValueError, OSError) as err:
        raise SnekRestartError(err) from err

    status = get_status(path, session_id or params.output.session_id)

    if verify_contents:
        if status.code >= 400:
            raise SnekRestartError(f"{status.code}: {status.message}")
        else:
            logger.info(f"{status.code}: {status.message}")

    # Load Simul class and parameters
    short_name = get_solver_short_name(path)

    try:
        Simul = import_cls_simul(short_name)
    except ImportError:
        raise ImportError(f"Cannot import Simul class of solver {short_name}")

    # Set restart file
    if use_start_from and use_checkpoint:
        raise SnekRestartError(
            "Options use_start_from and use_checkpoint are mutually exclusive. "
            "Use only one option at a time."
        )
    elif not use_start_from and not use_checkpoint:
        raise SnekRestartError(
            "No restart files were requested. "
            "This would result in a fresh simulation in a new session."
        )
    elif use_checkpoint:
        if use_checkpoint in (1, 2) and status in (
            SimStatus.OK,
            SimStatus.RESET_CONTENT,
        ):
            params.nek.chkpoint.chkp_fnumber = use_checkpoint
            params.nek.chkpoint.read_chkpt = True
        else:
            raise SnekRestartError(
                f"Restart checkpoint {use_checkpoint} is invalid / does not exist"
            )

    if hasattr(params, "output") and hasattr(params.output, "HAS_TO_SAVE"):
        params.output.HAS_TO_SAVE = True

    params.NEW_DIR_RESULTS = bool(new_dir_results)

    if use_start_from:
        if session_id is not None:
            old_path_session = _make_path_session(path, session_id)
        else:
            old_path_session = Path(params.output.path_session)
        try:
            index_start_from = int(use_start_from)
        except ValueError:
            path_start_from = old_path_session / use_start_from
        else:
            paths = sorted(old_path_session.glob(f"{short_name}0.*"))
            path_start_from = paths[index_start_from]
        params.nek.general._set_internal_attr("_path_start_from", path_start_from)

    name_restart_file = "init_state.restart"
    if new_dir_results:
        params.path_run = None
        params.output.path_session = None
        params.output.session_id = 0
        if use_start_from:
            params.nek.general.start_from = name_restart_file
            # new option Nek5000 master for interpolation on a new mesh
            # params.nek.general.start_from = name_restart_file + " int"
    else:
        new_session_id, new_path_session = next_path(
            path / "session", force_suffix=True, return_suffix=True
        )
        params.output.session_id = new_session_id
        params.output.path_session = new_path_session
        if not only_check:
            new_path_session.mkdir(exist_ok=True)

        if not only_check and use_start_from:
            if path_start_from.exists():
                params.nek.general.start_from = name_restart_file
                src = f"../{old_path_session.name}/{path_start_from.name}"
                dest = new_path_session / name_restart_file
                logger.debug(f"Symlinking {dest} -> {src}")
                dest.symlink_to(src)
            else:
                raise SnekRestartError(f"Restart file {path_start_from} not found")

    return params, Simul


class Restarter(RestarterABC):
    def create_parser(self):
        parser = super().create_parser()

        parser.add_argument(
            "-np",
            "--nb-mpi-procs",
            type=int,
            default=4,
            help="Number of MPI processes",
        )
        parser.add_argument(
            "--use-start-from",
            type=str,
            default=None,
            help=(
                "Name (relative to the session path) of the field file "
                "to restart from. "
                "Mutually exclusive option with `use_checkpoint`."
            ),
        )
        parser.add_argument(
            "--use-checkpoint",
            type=int,
            default=None,
            help=(
                "Number of the multi-file checkpoint file set to restart from. "
                "Mutually exclusive parameter with `use_start_from`."
            ),
        )
        parser.add_argument(
            "--session-id",
            type=int,
            default=None,
            help=(
                "Indicate which session directory should be used to look for "
                "restart files. If not specified it would default to the "
                "`path_session` value last recorded in the `params_simul.xml` file."
            ),
        )
        parser.add_argument(
            "--skip-verify-contents",
            action="store_true",
            help="Do not verify directory contents to avoid runtime errors.",
        )
        parser.add_argument(
            "--add-to-end-time",
            type=float,
            default=None,
            help="Time added to params.nek.general.end_time",
        )
        parser.add_argument(
            "--end-time",
            type=float,
            default=None,
            help="params.nek.general.end_time",
        )
        parser.add_argument(
            "--num-steps",
            type=int,
            default=None,
            help="params.nek.general.num_steps",
        )

        return parser

    _str_command_after_simul = dedent(
        """
        # To visualize with IPython:

        cd {path_run}; snek-ipy-load
    """
    )

    def _get_params_simul_class(self, args):
        if args.use_start_from is None and args.use_checkpoint is None:
            logger.error("Either --use-start-from or --use-checkpoint have to be given")
            sys.exit(1)
        return load_for_restart(
            args.path,
            use_start_from=args.use_start_from,
            use_checkpoint=args.use_checkpoint,
            session_id=args.session_id,
            verify_contents=not args.skip_verify_contents,
            new_dir_results=args.new_dir_results,
            only_check=args.only_check,
        )

    def _set_params_time_stepping(self, params, args):
        if args.num_steps is not None:
            params.nek.general.stop_at = "numSteps"
            params.nek.general.num_steps = int(args.num_steps)
        elif args.end_time is not None or args.add_to_end_time is not None:
            params.nek.general.stop_at = "endTime"
            if args.end_time is not None:
                end_time = args.end_time
            else:
                end_time = float(params.nek.general.end_time) + args.add_to_end_time
            params.nek.general.end_time = end_time

    def _start_sim(self, sim, args):
        if args.new_dir_results:
            if args.use_start_from:
                sim.create_symlink_start_from_file(
                    sim.params.nek.general._path_start_from
                )
            elif args.use_checkpoint:
                sim.create_symlinks_checkpoint_files(args.path)
        sim.make.exec("run_fg", nproc=args.nb_mpi_procs)

    def _check_params_time_stepping(self, params, path_file, args):
        args_times = [args.num_steps, args.end_time, args.add_to_end_time]
        if sum(arg is not None for arg in args_times) > 1:
            raise ValueError(
                "--add-to-end-time, --end-time and --num-steps are exclusive options."
            )

    def _get_path_restart_file(self, params, args):
        if args.use_start_from is not None:
            path_file = args.use_start_from
        elif args.use_checkpoint is not None:
            path_file = f"Use checkpoint files (use_checkpoint={args.use_checkpoint})"
        logger.info(path_file)
        return path_file


_restarter = Restarter()

create_parser = _restarter.create_parser


def main():
    _restarter.restart()


if "sphinx" in sys.modules:
    from textwrap import indent
    from unittest.mock import patch

    with patch.object(sys, "argv", ["snek-restart"]):
        parser = create_parser()

    __doc__ += """
Help message
------------

.. code-block::

""" + indent(
        parser.format_help(), "    "
    )
