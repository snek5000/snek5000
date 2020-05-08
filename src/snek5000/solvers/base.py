"""Nek5000 base solver
======================

A bare Nek5000 solver which does not rely on any user parameters.

"""
import math
from pathlib import Path
from warnings import warn

import numpy as np
from fluidsim.base.solvers.base import SimulBase
from fluidsim.base.solvers.info_base import create_info_simul

from .. import __version__, logger, mpi
from ..info import InfoSolverNek
from ..params import Parameters, create_params


class SimulNek(SimulBase):
    """Simulation class

    .. code-block:: python

       from snek5000.solvers.base import Simul
       params = Simul.create_default_params()
       sim = Simul(params)

    """

    InfoSolver = InfoSolverNek

    @classmethod
    def create_default_params(cls):
        """Generate default parameters. ``params.nek`` contains runtime
        parameters consumed by Nek5000.

        """
        cls.info_solver = cls.InfoSolver()
        cls.info_solver.complete_with_classes()
        return create_params(cls.info_solver)

    @classmethod
    def load_params_from_file(cls, path_xml=None, path_par=None):
        if not (path_xml or path_par):
            raise IOError("Either path to params.xml or case.par should be provided")

        params = Parameters(tag="params")
        if path_xml:
            params._load_from_xml_file(path_xml)
        else:
            logger.warn(
                "Loading from a par file will not have full details of the simulation"
            )
            params.nek._read_par(path_par)

        cls._set_internal_sections(params)
        return params

    @classmethod
    def _set_internal_sections(cls, params):
        try:
            info_solver = cls.info_solver
        except AttributeError:
            info_solver = cls.InfoSolver()

        for section in info_solver.par_sections:
            getattr(params.nek, section)._set_internal_attr("_user", False)

        for section in info_solver.par_sections_disabled:
            getattr(params.nek, section)._set_internal_attr("_enabled", False)

    @staticmethod
    def _complete_params_with_default(params):
        """A static method used to complete the *params* container.

        The sections are:

        * ``general`` (mandatory)
        * ``problemtype``
        * ``mesh``
        * ``velocity``
        * ``pressure`` (required for velocity)
        * ``temperature``
        * ``scalar%%``
        * ``cvode``

        When scalars are used, the keys of each scalar are defined under the section
        ``scalar%%`` varying between ``scalar01`` and ``scalar99``.

        """

        params._set_child("nek")
        params_nek = params.nek

        params._set_attribs(dict(NEW_DIR_RESULTS=True, short_name_type_run="run"))
        for section in ("general", "problemtype", "velocity", "pressure"):
            params_nek._set_child(section)

        for section in ("mesh", "temperature", "scalar01", "cvode"):
            params_nek._set_child(section)
            getattr(params_nek, section)._set_internal_attr("_enabled", False)

        SimulNek._set_internal_sections(params)

        params_nek.general._set_attribs(
            dict(
                start_from="",
                stop_at="numSteps",
                end_time=math.nan,
                num_steps=1,
                dt=math.nan,
                variable_dt=True,
                target_cfl=0.5,
                write_control="timeStep",
                write_interval=10,
                filtering=None,
                filter_cutoff_ratio=0.65,
                filter_weight=12.0,
                write_double_precision=True,
                dealiasing=True,
                time_stepper="BDF2",
                extrapolation="standard",
                opt_level=2,
                log_level=2,
                user_params={},
            )
        )

        params_nek.problemtype._set_attribs(
            dict(
                equation="incompNS",
                variable_properties=False,
                stress_formulation=False,
            )
        )
        common = dict(residual_tol=math.nan, residual_proj=False)
        params_nek.velocity._set_attribs(common)
        params_nek.pressure._set_attribs(common)
        params_nek.temperature._set_attribs(common)
        params_nek.scalar01._set_attribs(common)

        params_nek.velocity._set_attribs(dict(viscosity=math.nan, density=math.nan))
        params_nek.pressure._set_attrib("preconditioner", "semg_xxt")
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
            setattr(self, cls_name.lower(), Class(self))

        if "Output" in dict_classes:
            # path_run would be initialized by the Output instance if available
            # See self.output._init_name_run()
            self.path_run = Path(self.output.path_run)
            self.output.copy(self.path_run)
        else:
            par_file = None
            self.path_run = None
            if mpi.rank == 0:
                logger.warning("No output class initialized!")

        _banner_length = 42
        if mpi.rank == 0:
            logger.info("*" * _banner_length)
            logger.info(f"solver: {self.__class__}")
            logger.info(f"path_run: {self.path_run}")
            logger.info("*" * _banner_length)
            if self.path_run:
                par_file = self.path_run / f"{self.output.name_pkg}.par"
                logger.info(f"Writing params files... {par_file}, params.xml")
                with open(par_file, "w") as fp:
                    params.nek._write_par(fp)

                params._save_as_xml(
                    self.path_run / "params.xml", f"eTurb version {__version__}"
                )


Simul = SimulNek
