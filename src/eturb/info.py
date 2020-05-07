"""Information classes
======================

Store information regarding modules and class names of simulation class and
dependent objects.

"""
from fluidsim.base.solvers.info_base import InfoSolverBase


class InfoSolverNek(InfoSolverBase):
    """Contain the information on a :class:`eturb.solvers.base.Simul`
    instance.

    """

    def _init_root(self):
        self._set_attribs(
            {
                "module_name": "eturb.solvers.base",
                "class_name": "SimulNek",
                "short_name": "nek",
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
                "par_sections_disabled": (
                    "mesh",
                    "temperature",
                    "scalar01",
                    "cvode",
                ),
            }
        )
        self._set_child("classes")
        self.classes._set_child(
            "Oper",
            attribs={"module_name": "eturb.operators", "class_name": "Operators"},
        )


class InfoSolverABL(InfoSolverNek):
    """Contain the information on a :class:`eturb.solvers.abl.Simul`
    instance.
    
    .. todo::
    
        Move Output info to :class:`InfoSolverNek` and only override it in
        :class:`InfoSolverABL`.

    """

    def _init_root(self):
        super()._init_root()
        self.module_name = "eturb.solvers.abl"
        self.class_name = "SimulABL"
        self.short_name = "abl"

        self.classes._set_child(
            "Output", attribs={"module_name": "abl", "class_name": "Output"}
        )
        self.classes._set_child(
            "Make", attribs={"module_name": "eturb.make", "class_name": "Make"}
        )
