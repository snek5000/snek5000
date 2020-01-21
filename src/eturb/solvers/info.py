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
                "short_name": "Nek",
            }
        )
        self._set_child("classes")
        self.classes._set_child(
            "State", attribs={"module_name": "eturb.state", "class_name": "State"}
        )
