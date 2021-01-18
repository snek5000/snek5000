"""Nek5000 base solver
======================

A bare Nek5000 solver which does not rely on any user parameters.

"""
import math
from pathlib import Path

from fluidsim_core.solver import SimulCore
from inflection import underscore

from .. import logger, mpi
from ..info import InfoSolverNek
from ..params import Parameters


class SimulNek(SimulCore):
    """Simulation class

    Parameters
    ----------
    params: Parameters
        Input parameters for the simulation run.
    write_files: bool, optional
        Write simulation files, including usr, box, SIZE files. By default
        all files are written.

    Example
    -------
    >>> from snek5000.solvers.base import Simul
    >>> params = Simul.create_default_params()
    >>> sim = Simul(params)

    """

    InfoSolver = InfoSolverNek
    Parameters = Parameters

    @classmethod
    def create_default_params(cls):
        """Generate default parameters. ``params.nek`` contains runtime
        parameters consumed by Nek5000.

        """
        return super().create_default_params()

    @classmethod
    def load_params_from_file(cls, path_xml=None, path_par=None):
        if not (path_xml or path_par):
            raise IOError(
                "Either path to params_simul.xml or case.par should be provided"
            )

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
                filter_modes=2,
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
        common = dict(
            residual_tol=math.nan, residual_proj=False, write_to_field_file=True
        )
        params_nek.velocity._set_attribs(common)
        params_nek.pressure._set_attribs(common)
        params_nek.temperature._set_attribs(common)
        params_nek.scalar01._set_attribs(common)

        common_ts = dict(solver="helm", advection=True, absolute_tol=math.nan)
        params_nek.temperature._set_attribs(common_ts)
        params_nek.scalar01._set_attribs(common_ts)

        params_nek.mesh._set_attrib("write_to_field_file", True)
        params_nek.velocity._set_attribs(dict(viscosity=math.nan, density=math.nan))
        params_nek.pressure._set_attrib("preconditioner", "semg_xxt")
        params_nek.temperature._set_attribs(
            dict(
                conjugate_heat_transfer=False,
                conductivity=math.nan,
                rho_cp=math.nan,
            )
        )
        params_nek.scalar01._set_attribs(dict(density=math.nan, diffusivity=math.nan))
        return params

    def __init__(self, params):
        super().__init__(params)

        dict_classes = self.info_solver.import_classes()

        # initialize objects
        for cls_name, Class in dict_classes.items():
            # only initialize if Class is not the Simul class
            if not isinstance(self, Class):
                setattr(self, underscore(cls_name), Class(self))

        if "Output" in dict_classes:
            if not params.NEW_DIR_RESULTS:
                self.path_run = self.output.path_run = Path(params.path_run)
            else:
                # path_run would be initialized by the Output instance if available
                # See self.output._init_name_run()
                self.path_run = Path(self.output.path_run)

            self.output.post_init()
        else:
            self.path_run = None
            if mpi.rank == 0:
                logger.warning("No output class initialized!")


Simul = SimulNek
