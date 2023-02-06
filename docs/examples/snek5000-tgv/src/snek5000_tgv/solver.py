from math import pi
from pathlib import Path

from snek5000.info import InfoSolverMake
from snek5000.params import complete_params_from_par_file
from snek5000.solvers.base import SimulNek


class InfoSolverTGV(InfoSolverMake):
    """Contain the information on a :class:`snek5000_tgv.solver.Simul`
    instance.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "snek5000_tgv.solver"
        self.class_name = "Simul"
        self.short_name = "tgv"

        self.classes.Output.module_name = "snek5000_tgv.output"
        self.classes.Output.class_name = "OutputTGV"


class SimulTGV(SimulNek):
    """A solver which compiles and runs using a Snakefile."""

    InfoSolver = InfoSolverTGV

    @classmethod
    def create_default_params(cls):
        """Set default values of parameters as given in reference
        implementation.

        """
        params = super().create_default_params()
        # Re-define default values for parameters here, if necessary

        # Mesh: from ms0.box and SIZE files
        params.oper.Lx = params.oper.Ly = params.oper.Lz = 2 * pi
        params.oper.nx = params.oper.ny = params.oper.nz = 8
        params.oper.elem.order = params.oper.elem.order_out = 8
        params.oper.elem.staggered = False

        # Snek5000 also has a human-friendly interface for userParams## parameter in the par file
        # Here we map the mesh length to userParam01, which is used in subroutine usrdat
        params.oper._record_nek_user_params({"Lx": 1})

        # Read defaults for `params.nek` from `tgv.par.cfg` (original code)
        complete_params_from_par_file(
            params,
            Path(__file__).parent / f"{cls.info_solver.short_name}.par.cfg",
        )

        # Boundary conditions
        # Symmetric on top and bottom; periodic on all 6 faces
        params.oper.boundary = ["P"] * 6

        # NOTE: These are only default parameters for a minimal simulation -
        # which can be verify different for another case. Modifications to
        # ``params`` by the user in a separate script are also encouraged.
        return params


Simul = SimulTGV
