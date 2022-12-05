"""Nek5000 base solver
======================

A bare Nek5000 solver which does not rely on any user parameters.

"""
import math
import textwrap
from pathlib import Path

from inflection import underscore

from fluidsim_core.solver import SimulCore

from .. import logger, mpi
from ..info import InfoSolverNek
from ..params import (
    Parameters,
    _complete_params_from_xml_file,
    complete_params_from_par_file,
)
from ..util import docstring_params


class SimulNek(SimulCore):
    """Simulation class

    Parameters
    ----------

    params: Parameters
        Input parameters for the simulation run.
    write_files: bool, optional
        Write simulation files, including usr, box, SIZE files. By default
        all files are written.

    Examples
    --------

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
        """Instantiate a Parameters instance and populate it from
        `params_simul.xml` or `case.par`

        """
        if not (path_xml or path_par):
            raise IOError(
                "Either path to params_simul.xml or case.par should be provided"
            )

        if path_xml:
            params = Parameters(tag="params")
            _complete_params_from_xml_file(params, path_xml)
        else:
            logger.warn(
                "Loading from a par file will not have full details of the simulation"
            )
            params = cls.create_default_params()
            complete_params_from_par_file(params, path_par)

        cls._set_internal_sections(params)
        return params

    @classmethod
    def _set_internal_sections(cls, params):
        """Set internal attributes to mark user sections and disable sections
        following :attr:`InfoSolverNek.par_sections_disabled`. The internal
        attributes  ``_user`` and ``_enabled`` of :class:`Parameters` are
        modified here.

        """
        try:
            info_solver = cls.info_solver
        except AttributeError:
            info_solver = cls.InfoSolver()

        for section in info_solver.par_sections:
            getattr(params.nek, section)._set_internal_attr("_user", False)

        for section in info_solver.par_sections_disabled:
            getattr(params.nek, section)._set_internal_attr("_enabled", False)

    @classmethod
    def _complete_params_with_default(cls, params):
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

        params_nek._set_doc(
            textwrap.dedent(
                """
    The parameters in ``params.nek`` are used by Snek to produce the Nek file
    .par, which is documented here :ref:`nek:case_files_par`.

    .. note::

        For these parameters, there is nearly a direct correspondance between
        Nek5000 par file keys and Snek5000 parameter variable names, with only
        *camelCase* <-> *snake_case* conversions. This is
        implemented in :mod:`snek5000.params`.

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

    There is a mechanism to enable/disable these sections so that they are used
    or not to produce the .par file (see our `tutorial on writting new solvers
    <https://snek5000.readthedocs.io/en/latest/packaging.html>`__).
"""
            )
        )

        params._set_attribs(dict(NEW_DIR_RESULTS=True, short_name_type_run="run"))

        # Referenced using Sphinx extension intersphinx. Run make intersphinx-nek in docs to see available labels
        table_in_nek_doc = {
            "general": "tab:generalparams",
            "problemtype": "tab:probtypeparams",
            "velocity": "tab:velocityparams",
            "pressure": "tab:pressureparams",
            "mesh": "tab:meshparams",
            "temperature": "tab:temperatureparams",
            "scalar01": "tab:scalarparams",
            "cvode": "tab:cvodeparams",
        }

        for section in (
            "general",
            "problemtype",
            "velocity",
            "pressure",
            "mesh",
            "temperature",
            "scalar01",
            "cvode",
        ):
            child = params_nek._set_child(section)

            child._set_doc(
                f"""
    See table :ref:`nek:{table_in_nek_doc[section]}`
"""
            )

        cls._set_internal_sections(params)

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

        # Document all params
        for child_name in params.nek._tag_children:
            child = getattr(params.nek, child_name)
            child._autodoc_par(indent=4)

        return params

    def __init__(self, params):
        super().__init__(params)

        self._objects_to_print = "{:28s}{}\n".format("sim: ", type(self))
        dict_classes = self.info_solver.import_classes()

        # initialize objects
        for cls_name, Class in dict_classes.items():
            # only initialize if Class is not the Simul class
            if not isinstance(self, Class):
                obj_name = underscore(cls_name)
                setattr(self, obj_name, Class(self))
                self._objects_to_print += "{:28s}{}\n".format(
                    f"sim.{obj_name}: ", Class
                )

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

    def create_symlink_start_from_file(self, path):
        """Create a symlink towards the start_from file"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist.")
        path_session = Path(self.output.path_session)
        path_session.mkdir(exist_ok=True)
        dest = path_session / self.params.nek.general.start_from
        if dest.exists():
            raise FileExistsError(f"{dest} already exists.")
        logger.info(f"Symlinking {path} -> {dest}")
        dest.symlink_to(path)


Simul = SimulNek
Simul.__doc__ += """

    Notes
    -----

    Here, only the documention for ``params.nek`` is displayed. For the
    documentation on ``params.oper`` see :mod:`snek5000.operators`.

""" + docstring_params(
    Simul, indent_len=4
)
