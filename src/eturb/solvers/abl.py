from ..info import InfoSolverABL
from .base import SimulNek


class SimulABL(SimulNek):
    InfoSolver = InfoSolverABL


Simul = SimulABL
