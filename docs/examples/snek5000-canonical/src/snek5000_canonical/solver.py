from snek5000.info import InfoSolverMake
from snek5000.solvers.base import SimulNek

# To use KTH Framework import SimulKTH instead
# from snek5000.solvers.kth import SimulKTH


class InfoSolverCanonical(InfoSolverMake):
    """Contain the information on a :class:`snek5000_canonical.solver.Simul`
    instance.

    """

    def _init_root(self):
        from . import short_name

        super()._init_root()
        self.module_name = "snek5000_canonical.solver"
        self.class_name = "Simul"
        self.short_name = short_name

        self.classes.Output.module_name = "snek5000_canonical.output"
        self.classes.Output.class_name = "OutputCanonical"

        # To solve for the temperature, one needs to add a [TEMPERATURE]
        # section in the .par file. It can be done like this:
        self.par_sections_disabled.remove("temperature")


class SimulCanonical(SimulNek):
    """A solver which compiles and runs using a Snakefile."""

    InfoSolver = InfoSolverCanonical

    @classmethod
    def create_default_params(cls):
        """Set default values of parameters as given in reference
        implementation.

        """
        params = super().create_default_params()
        # Re-define default values for parameters here, if necessary
        # following ``canonical.par``, ``canonical.box`` and ``SIZE`` files

        # Extend with new default parameters here, for example:
        # params.nek.velocity._set_attrib("advection", True)

        return params


Simul = SimulCanonical
