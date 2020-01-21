"""Nek5000 base solver
======================

A bare Nek5000 solver which does not rely on any user parameters.

"""
import math
from warnings import warn

import numpy as np
from fluidsim.base.solvers.base import SimulBase
from fluidsim.base.solvers.info_base import create_info_simul

from ..params import Parameters
from .info import InfoSolverNek


class SimulNek(SimulBase):
    """Simulation class

    .. code-block:: python

       from eturb.solvers.base import Simul
       params = Simul.create_default_params()
       sim = Simul(params)

    """
    InfoSolver = InfoSolverNek

    @classmethod
    def create_default_params(cls):
        """Generate default parameters. ``params.nek`` contains runtime
        parameters consumed by Nek5000.

        """
        tag = "base"
        cls.info_solver = cls.InfoSolver()
        cls.info_solver.complete_with_classes()
        params = Parameters(tag=tag)

        params._set_child("nek")
        params_nek = params.nek

        for section in ("GENERAL", "PROBLEMTYPE", "VELOCITY", "PRESSURE"):
            params_nek._set_child(section, {"_enabled": True})
            params._par_file.add_section(section)

        for section in (
            "MESH",
            "TEMPERATURE",
            "SCALAR01",
            "CVODE",
        ):
            params_nek._set_child(section, {"_enabled": False})

        params_nek._set_doc(
            """
The sections are:

* ``GENERAL`` (mandatory)
* ``PROBLEMTYPE``
* ``MESH``
* ``VELOCITY``
* ``PRESSURE`` (required for velocity)
* ``TEMPERATURE``
* ``SCALAR%%``
* ``CVODE``

When scalars are used, the keys of each scalar are defined under the section
``SCALAR%%`` varying between ``SCALAR01`` and ``SCALAR99``.
"""
        )
        params_nek.GENERAL._set_attribs(
            dict(
                startFrom="",
                stopAt="numSteps",
                endTime=math.nan,
                numSteps=1,
                dt=math.nan,
                variableDT=True,
                targetCFL=0.5,
                writeControl="timeStep",
                writeInterval=10,
                filtering=None,
                filterCutoffRatio=0.65,
                filterWeight=12.0,
                writeDoublePrecision=True,
                dealiasing=True,
                timeStepper="BDF2",
                extrapolation="standard",
                optLevel=2,
                loglevel=2,
                userParam03=1,
            )
        )
        params_nek.PROBLEMTYPE._set_attribs(
            dict(
                equation="incompNS",
                variableProperties=False,
                stressFormulation=False,
            )
        )
        common = dict(residualTol=math.nan, residualProj=False,)
        params_nek.VELOCITY._set_attribs(common)
        params_nek.PRESSURE._set_attribs(common)
        params_nek.TEMPERATURE._set_attribs(common)
        params_nek.SCALAR01._set_attribs(common)

        params_nek.VELOCITY._set_attribs(
            dict(viscosity=math.nan, density=math.nan)
        )
        params_nek.PRESSURE._set_attrib("preconditioner", "semg_xxt")
        return params

    def __init__(self, params):
        np.seterr(all="warn")
        np.seterr(under="ignore")

        if (
            not hasattr(self, "info_solver")
            or self.info_solver.__class__ is not self.InfoSolver
        ):
            if hasattr(self, "info_solver"):
                warn(
                    "Creating a new info_solver instance "
                    f"due to type mismatch  {self.InfoSolver}"
                )
            self.info_solver = self.InfoSolver()
            self.info_solver.complete_with_classes()

        dict_classes = self.info_solver.import_classes()

        if not isinstance(params, Parameters):
            raise TypeError(
                f"params should be a Parameters instance, not {type(params)}"
            )

        self.params = params
        self.info = create_info_simul(self.info_solver, params)
        # initialize objects
        for cls_name, Class in dict_classes.items():
            setattr(self, cls_name, Class(self))


Simul = SimulNek
