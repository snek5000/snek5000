from .base import SimulNek
from .info import InfoSolverABL


class SimulABL(SimulNek):
    InfoSolver = InfoSolverABL


Simul = SimulABL
