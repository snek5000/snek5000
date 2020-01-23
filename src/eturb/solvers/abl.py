"""ABL solver
=============

A solver which specifically deals with the ABL case files.

"""
from abl import get_root

from .. import logger, mpi
from ..info import InfoSolverABL
from .base import SimulNek


class SimulABL(SimulNek):
    InfoSolver = InfoSolverABL

    @staticmethod
    def _complete_params_with_default(params):
        params = SimulNek._complete_params_with_default(params)

        # Synchronize baseline parameters
        primary_par_file = get_root() / "abl.par"
        if mpi.rank == 0:
            logger.info(f"Reading baseline parameters from {primary_par_file}")
        params._read_par(primary_par_file)

        return params


Simul = SimulABL
