"""KTH base solver
==================

"""
from pathlib import Path

# NOTE: Ideally InfoSolverMake should be used. Here, this won't work because
# user files are missing.
# from ..info import InfoSolverMake as _InfoSolver
from .. import logger
from ..info import InfoSolverNek as _InfoSolver
from ..util import docstring_params
from .base import SimulNek


class InfoSolverKTH(_InfoSolver):
    """Contain the information on a :class:`snek5000.solvers.kth.SimulKTH`
    instance.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "snek5000.solvers.kth"
        self.class_name = "Simul"
        self.short_name = "kth"


class SimulKTH(SimulNek):
    """A base class which incorporates parameters for KTH toolbox also.

    Examples
    --------

    >>> from snek5000.solvers.kth import Simul
    >>> params = Simul.create_default_params()
    >>> sim = Simul(params)

    """

    InfoSolver = InfoSolverKTH

    @classmethod
    def _complete_params_with_default(cls, params):
        params = super()._complete_params_with_default(params)

        for section in ("runpar", "monitor", "chkpoint", "stat"):
            params.nek._set_child(section)

        attribs = {"parf_write": False, "parf_name": "outparfile"}
        params.nek.runpar._set_attribs(attribs)
        params.nek.runpar._set_doc(
            """
    Runtime parameter section for rprm module (`KTH toolbox <https://github.com/KTH-Nek5000/KTH_Toolbox>`__)

    - ``parf_write``: Do we write runtime parameter file
    - ``parf_name``: Runtime parameter file name for output (without .par)
"""
        )

        attribs = {"log_level": 4, "wall_time": "23:45"}
        params.nek.monitor._set_attribs(attribs)
        params.nek.monitor._set_doc(
            """
    Runtime parameter section for monitor module (`KTH toolbox <https://github.com/KTH-Nek5000/KTH_Toolbox>`__)

    - ``log_level``: Logging threshold for toolboxes
    - ``wall_time``: Simulation wall time
"""
        )

        attribs = {"read_chkpt": False, "chkp_fnumber": 1, "chkp_interval": 250}
        params.nek.chkpoint._set_attribs(attribs)
        params.nek.chkpoint._set_doc(
            """
    Runtime parameter section for checkpoint module (`KTH toolbox <https://github.com/KTH-Nek5000/KTH_Toolbox>`__)

    - ``read_chkpt``: Restart from checkpoint
    - ``chkp_fnumber``: Restart file number
    - ``chkp_interval``: Checkpoint saving frequency (number of time steps)
"""
        )

        attribs = {"av_step": 4, "io_step": 50}
        params.nek.stat._set_attribs(attribs)
        params.nek.stat._set_doc(
            """
    Runtime parameter section for statistics module (`KTH toolbox <https://github.com/KTH-Nek5000/KTH_Toolbox>`__)

    - ``av_step``: Frequency of averaging
    - ``io_step``: Frequency of file saving
"""
        )

        # Document all params
        for child_name in ("runpar", "monitor", "chkpoint", "stat"):
            child = getattr(params.nek, child_name)
            child._autodoc_par(indent=4)

        return params

    def create_symlinks_checkpoint_files(self, path_run):
        """Create symlinks towards checkpoint files"""
        paths = sorted(Path(path_run).glob("rs6*"))
        if not paths:
            raise FileNotFoundError("No restart file in {path_run}")
        logger.info("Symlinking checkpoint files")
        for src in paths:
            dest = Path(self.output.path_run) / src.name
            dest.symlink_to(src)


Simul = SimulKTH
Simul.__doc__ += """

    Notes
    -----

    Here, only the documention for ``params.nek`` is displayed. For the
    documentation on ``params.oper`` see :mod:`snek5000.operators`.

""" + docstring_params(
    Simul, indent_len=4
)
