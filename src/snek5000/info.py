"""Information classes
======================

Store information regarding modules and class names of simulation class and
dependent objects.

"""
from fluidsim_core.info import InfoSolverCore


class InfoSolverNek(InfoSolverCore):
    """Contain the information on a :class:`snek5000.solvers.base.Simul`
    instance.

    """

    def _init_root(self):
        """Defines class hierarchy (via :attr:`classes`) and some attributes

        - :attr:`module_name` - module of the Simul class
        - :attr:`class_name` - Simul class name
        - :attr:`short_name` - short name of the solver (and name used in the
          source code usr, par, re2, ma2 etc.)
        - :attr:`par_sections` - sections in the .par file
        - :attr:`par_sections_disabled` - sections to be disabled (i.e. removed
          while generating) in the .par file

        """
        self._set_attribs(
            {
                "module_name": "snek5000.solvers.base",
                "class_name": "SimulNek",
                "short_name": "nek",
                "loader": "snek5000.load",
                "par_sections": (
                    "general",
                    "problemtype",
                    "velocity",
                    "pressure",
                    "mesh",
                    "temperature",
                    "scalar01",
                    "cvode",
                ),
                "par_sections_disabled": {
                    "mesh",
                    "temperature",
                    "scalar01",
                    "cvode",
                },
            }
        )
        self._set_child("classes")
        self.classes._set_child(
            "Oper",
            attribs={
                "module_name": "snek5000.operators",
                "class_name": "Operators",
            },
        )


class InfoSolverMake(InfoSolverNek):
    """Contain the information on a solver which uses Snakemake."""

    def _init_root(self):
        super()._init_root()
        self.classes._set_child(
            "Output",
            attribs={
                "module_name": "snek5000.output.base",
                "class_name": "Output",
            },
        )
        self.classes._set_child(
            "Make", attribs={"module_name": "snek5000.make", "class_name": "Make"}
        )
