"""Base class for ``sim.output``.

"""
import inspect
import logging
import os
import pkgutil
import shutil
import stat
import textwrap
import warnings
from importlib import resources
from itertools import chain
from pathlib import Path
from socket import gethostname

import yaml
from inflection import underscore

from fluiddyn.io import stdout_redirected
from fluiddyn.util import mpi
from fluidsim_core.output import OutputCore
from fluidsim_core.params import iter_complete_params
from snek5000 import __version__, get_snek_resource, logger
from snek5000.make import _Nek5000Make
from snek5000.params import _save_par_file
from snek5000.solvers import get_solver_package, is_package
from snek5000.util import docstring_params
from snek5000.util.files import bisect_nek_files_by_time
from snek5000.util.smake import append_debug_flags, set_compiler_verbosity

from . import _make_path_session


class MissingConfigFilter:
    def filter(self, record):
        msg = record.msg
        if hasattr(msg, "startswith") and msg.startswith(
            "Missing a configuration file"
        ):
            if hasattr(self, "emitted") and self.emitted:
                return False
            self.emitted = True
        return True


missing_config_filter = MissingConfigFilter()
logger.addFilter(missing_config_filter)


class Output(OutputCore):
    """Container and methods for getting paths of and copying case files.

    Some important methods:

    - :meth:`snek5000.output.base.Output.get_path_solver_package` points to the
      directory containing the case files.
    - :meth:`snek5000.output.base.Output.get_paths` populates a list of
      files to copy.

    and important attributes:

    .. autoattribute:: name_solver
       :noindex:

        Initialized from ``sim.info.solver.short_name`` used to discover source
        code files, such as usr, box, par files. The value of ``name_solver``
        is also used to identify the entrypoint pointing to the solver module.
        Have a look at the :ref:`packaging tutorial <packaging>`.

    .. autoattribute:: package

        Initialized using :func:`snek5000.solvers.get_solver_package` and
        :attr:`name_solver`, points to the path to the package to discover
        source code files.

    .. autoattribute:: path_run
       :noindex:

        Path to the generated simulation directory.

    .. autoattribute:: path_session

        Path to subdirectory under :attr:`path_run` which would contain the
        field files upon execution. This path would be written into the
        `SESSION.NAME` file.

    """

    _config_filename = "config_simul.yml"

    @property
    def excludes(self):
        """Prefixes and suffixes of files which should be excluded from being
        copied."""
        return {
            "prefix": "__",
            "suffix": (".vimrc", ".tar.gz", ".o", ".py", ".usr.f", ".par.cfg"),
        }

    @property
    def makefile_usr_sources(self):
        """
        Sources for inclusion to makefile_usr.inc
        Dict[directory]  -> list of source files
        """
        return {
            # "source_directory": [
            #    (src1a.f, src1b.f)
            #    (src2a.f, src2b.f, src2c.f), ...
            # ]
        }

    @property
    def makefile_usr_obj(self):
        """Object files to be included in compilation. Should be exported as USR
        environment variable.

        """
        makefile_usr_obj = [
            sources[0].replace(".f", ".o")
            for sources in chain.from_iterable(self.makefile_usr_sources.values())
        ]
        return makefile_usr_obj

    @property
    def fortran_inc_flags(self):
        return (f"-I{inc_dir}" for inc_dir in self.makefile_usr_sources)

    @classmethod
    def _set_info_solver_classes(cls, classes):
        """Set the the classes for info_solver.classes.Output"""

        classes._set_child(
            "PrintStdout",
            dict(
                module_name="snek5000.output.print_stdout",
                class_name="PrintStdOut",
            ),
        )
        classes._set_child(
            "PhysFields",
            dict(module_name="snek5000.output.phys_fields", class_name="PhysFields"),
        )

        classes._set_child(
            "HistoryPoints",
            dict(
                module_name="snek5000.output.history_points",
                class_name="HistoryPoints",
            ),
        )

        classes._set_child(
            "RemainingClockTime",
            dict(
                module_name="snek5000.output.remaining_clock_time",
                class_name="RemainingClockTime",
            ),
        )

    @classmethod
    def _complete_info_solver(cls, info_solver):
        """Complete the info_solver instance with child class details (module
        and class names).

        """
        classes = info_solver.classes.Output._set_child("classes")
        cls._set_info_solver_classes(classes)
        # iteratively call _complete_info_solver of the above classes
        info_solver.classes.Output.complete_with_classes()

    @staticmethod
    def _complete_params_with_default(params, info_solver):
        """This static method is used to complete the *params* container."""

        # Bare minimum
        attribs = {
            "HAS_TO_SAVE": True,
            "sub_directory": "",
            "session_id": 0,
        }
        params._set_child("output", attribs=attribs)
        params.output._set_doc(
            textwrap.dedent(
                """
    - ``HAS_TO_SAVE``: bool (default: True) If False, nothing new is saved in
      the directory of the simulation.
    - ``sub_directory``: str (default: "") A name of a sub-directory (relative
      to $FLUIDDYN_PATH_SCRATCH) wherein the directory of the simulation
      (``path_run``) is saved.
    - ``session_id``: int (default: 0) Determines the sub-directory,
      ``path_session`` in which the field files would be generated during
      runtime. The session directory takes the form `session_{session_id}`.

    .. note::

        In short, the field files would be generated under
        ``$FLUIDDYN_PATH_SCRATCH/<path_run>/<path_session>``

"""
            )
        )

        dict_classes = info_solver.classes.Output.import_classes()
        iter_complete_params(params, info_solver, dict_classes.values())

    @classmethod
    def get_path_solver_package(cls):
        """Get the path towards the solver package."""
        return Path(inspect.getmodule(cls).__file__).parent

    @classmethod
    def find_configfile(cls, host=None) -> Path:
        """Get path of the Snakemake configuration file for the current machine.
        All configuration files are stored under ``etc`` sub-package.

        Parameters
        ----------
        host: str
            Override hostname detection and specify it instead

        """
        if not host:
            host = os.getenv(
                "SNIC_RESOURCE", os.getenv("GITHUB_WORKFLOW", gethostname())
            )
        path_solver_package = cls.get_path_solver_package()
        xdg_config = Path(
            os.path.expandvars(os.getenv("XDG_CONFIG_HOME", "$HOME/.config"))
        )
        configfile_root = path_solver_package / "etc" / f"{host}.yml"
        configfile_xdg_config_host = xdg_config / f"snek5000/{host}.yml"
        configfile_xdg_config = xdg_config / "snek5000.yml"
        configfile_default = Path(get_snek_resource("default_configfile.yml"))

        custom_configfiles = (
            configfile_xdg_config_host,
            configfile_xdg_config,
            configfile_root,
        )

        for configfile in custom_configfiles:
            if configfile.exists():
                break
        else:
            configfile = configfile_default
            logger.warning(
                (
                    "Missing a configuration file describing compilers and "
                    "flags. Create one at either of the following paths to "
                    "avoid future warnings:\n"
                )
                + "\n".join(map(str, custom_configfiles))
                + "\nThe command `snek-generate-config` could be used to create "
                "a user config file for you."
                f"\nUsing default configuration for now:\n{configfile}"
            )

        return configfile

    @classmethod
    def update_snakemake_config(
        cls, config, name_solver, /, verbosity=0, env_sensitive=None, **kwargs
    ):
        """Update snakemake config in-place with name of the solver / case,
        path to configfile and compiler flags

        Parameters
        ----------
        config: dict
            Snakemake configuration
        name_solver: str
            Short name of the solver, also known as case name
        verbosity: int
            Set compiler verbosity level. See :func:`snek5000.util.smake.set_compiler_verbosity`
        env_sensitive: bool (None)
            If ``False``, the ``config`` dictionary is not modified (allows for
            reproducible runs). If ``True``, the ``config`` dictionary is
            modified based on environment variables. If ``None`` (default), the
            value of ``env_sensitive`` is obtained with
            ``os.environ.get("SNEK_UPDATE_CONFIG_ENV_SENSITIVE", False)``.

        .. deprecated:: 0.8.0

            The ``warnings`` parameter is deprecated! Use ``verbosity=0`` (now default)
            to disable warnings. If you need ``warnings=True``, similar behaviour can
            be obtained by ``verbosity=1`` or ``verbosity=2``.

        """
        mandatory_config = {
            "CC",
            "FC",
            "MPICC",
            "MPIFC",
            "MPIEXEC",
            "MPIEXEC_FLAGS",
            "CFLAGS",
            "FFLAGS",
        }
        missing_config = mandatory_config - set(config)

        if missing_config:
            raise ValueError(
                f"Some keys are missing from the configfile "
                f"{cls.find_configfile()}: {missing_config}"
            )

        try:
            # Suppress warnings for not instantiating Output with sim or params
            logging_level = logger.getEffectiveLevel()
            logger.setLevel(logging.ERROR)
            temp = cls()
        finally:
            logger.setLevel(logging_level)

            config.update(
                {
                    "CASE": name_solver,
                    "file": Path(cls._config_filename).resolve(),
                    "includes": " ".join(temp.fortran_inc_flags),
                    "objects": " ".join(temp.makefile_usr_obj),
                }
            )

            if "warnings" in kwargs:
                warnings.warn(
                    "Parameter warnings is deprecated, use ``verbosity`` instead/",
                    DeprecationWarning,
                )
                verbosity = int(kwargs["warnings"])

            set_compiler_verbosity(config, verbosity)
            append_debug_flags(config)

            if env_sensitive is None:
                env_sensitive = os.environ.get(
                    "SNEK_UPDATE_CONFIG_ENV_SENSITIVE", False
                )
                if isinstance(env_sensitive, str):
                    # correct for "0", "false", "False"
                    env_sensitive = bool(yaml.safe_load(env_sensitive))

            if env_sensitive:
                logger.info(
                    "env_sensitive = True => attempting to update config from environment variables."
                )
                config.update(
                    {
                        key: os.getenv(key, original_value)
                        for key, original_value in config.items()
                    }
                )

    def __init__(self, sim=None, params=None):
        self.sim = sim
        try:
            self.name_solver = sim.info.solver.short_name
        except AttributeError:
            pass
        else:
            self.package = get_solver_package(self.name_solver)

        self.path_solver_package = self.get_path_solver_package()

        if sim:
            self.oper = sim.oper
            self.params = sim.params.output
            # Same as package name __name__
            super().__init__(sim)
        elif params:
            # At least initialize params
            self.params = params.output
        else:
            self.params = None
            logger.warning(
                "Initializing Output class without sim or params might lead to errors."
            )

        self.path_session = self._init_path_session()

        if sim:
            # initialize objects
            dict_classes = sim.info.solver.classes.Output.import_classes()
            for cls_name, Class in dict_classes.items():
                # only initialize if Class is not the Output class
                if not isinstance(self, Class):
                    obj_name = underscore(cls_name)
                    setattr(self, obj_name, Class(self))
                    self.sim._objects_to_print += "{:28s}{}\n".format(
                        f"sim.output.{obj_name}: ", Class
                    )

    def _init_path_session(self):
        """Initialize :attr:`path_session` and ``params.output.path_session``
        from ``params.output.session_id``. Unlike :meth:`_init_path_run`, the
        directory will not be created.

        Returns
        -------
        path_session: path-like

        """
        if not self.params or not hasattr(self, "path_run"):
            logger.debug("Attribute sim.output.path_session will not be initialized.")
            return None

        try:
            session_id = self.params.session_id
        except AttributeError:
            # For compatibility while loading old simulations
            path_session = Path(self.path_run)
            logger.warning(
                "Parameter params.output.session_id is undefined. "
                "Attribute sim.output.path_session is set as sim.output.path_run."
            )
        else:
            path_session = _make_path_session(self.path_run, session_id)

        self.params._set_attrib("path_session", path_session)

        return path_session

    def _init_sim_repr_maker(self):
        """Adds mesh description to name of the simulation. Called by the
        ``_init_name_run`` method"""
        sim_repr_maker = super()._init_sim_repr_maker()
        self.oper._modify_sim_repr_maker(sim_repr_maker)

        return sim_repr_maker

    def _get_resources(self, package=None):
        """Get a generator of resources (files) in a package, excluding
        directories (subpackages).

        :returns: generator

        """
        excludes = self.excludes
        if not package:
            package = self.package

        try:
            contents_pkg = resources.contents(package)
        except ImportError:
            raise FileNotFoundError(
                f"Cannot resolve subpackage name_solver={package} "
                f"at path_solver_package={self.path_solver_package}"
            )

        return (
            f
            for f in contents_pkg
            if (
                resources.is_resource(package, f)
                and not any(f.startswith(ext) for ext in excludes["prefix"])
                and not any(f.endswith(ext) for ext in excludes["suffix"])
            )
        )

    def _get_subpackages(self):
        """Get a dictionary of subpackages with values generated by
        :meth:`_get_resources`.

        :returns: dict

        """
        root = self.path_solver_package
        subpackages = {
            subpkg.name.replace(f"{root.name}.", ""): self._get_resources(subpkg.name)
            for subpkg in pkgutil.walk_packages([str(root)], prefix=f"{self.package}.")
            if is_package(subpkg)
        }

        return subpackages

    def get_paths(self):
        """Get a list of paths to all case files.

        :returns: list

        """
        paths = []

        # abl.usr -> /path/to/abl/abl.usr
        paths += [
            self.path_solver_package / resource for resource in self._get_resources()
        ]

        for subpkg, res in self._get_subpackages().items():
            # toolbox -> /path/to/abl/toolbox
            subpkg_root = self.path_solver_package / subpkg.replace(".", os.sep)
            # main.f -> /path/to/abl/toolbox/main.f
            paths += [subpkg_root / resource for resource in res]
        return paths

    def copy(self, new_dir, force=False):
        """Copy case files to a new directory. The directory does not have to be present.

        :param new_dir: A str or Path-like instance pointing to the new directory.
        :param force: Force copy would overwrite if files already exist.

        """
        # Avoid race conditions! Should be only executed by rank 0.
        if mpi.rank != 0:
            return

        abs_paths = self.get_paths()
        subpackages = self._get_subpackages()

        path_solver_package = self.path_solver_package

        def conditional_ignore(src, names):
            """Ignore if not found in ``abs_paths``."""
            src = Path(src)
            include = abs_paths + [
                path_solver_package / subpkg for subpkg in subpackages
            ]
            exclude = tuple(
                name
                for name in names
                if not any((src / name) == path for path in include)
            )

            logger.debug(
                "".join(
                    (
                        f"- src: {src}",
                        "\n- include:",
                        " ".join(Path(i).name for i in include),
                        "\n- exclude:",
                        " ".join(Path(i).name for i in exclude),
                    )
                )
            )
            return exclude

        new_root = Path(new_dir)
        # `dirs_exist_ok`` new in Python 3.8
        shutil.copytree(
            src=path_solver_package,
            dst=new_root,
            symlinks=False,
            ignore=conditional_ignore,
            dirs_exist_ok=True,
        )

        # special case for .usr.f: copy to .usr
        paths_usr_f = list(path_solver_package.glob("*.usr.f"))
        for path_usr_f in paths_usr_f:
            shutil.copyfile(path_usr_f, new_root / path_usr_f.stem)

    def write_box(self, template):
        """Write <case name>.box file from box.j2 template.

        .. seealso::
            :ref:`nek:tools_genbox`

        """
        if mpi.rank == 0:
            box_file = self.sim.path_run / f"{self.name_solver}.box"
            logger.info(f"Writing box file... {box_file}")
            with open(box_file, "w") as fp:
                self.sim.oper.write_box(
                    template, fp, comments=self.sim.params.short_name_type_run
                )

    def write_size(self, template):
        """Write SIZE file from SIZE.j2 template.

        .. seealso::

            Nek5000 docs on :ref:`nek:case_files_size`

        """
        if mpi.rank == 0:
            size_file = self.sim.path_run / "SIZE"
            logger.info(f"Writing SIZE file... {size_file}")
            with open(size_file, "w") as fp:
                self.oper.write_size(
                    template, fp, comments=self.sim.params.short_name_type_run
                )

    def write_makefile_usr(self, template, fp=None, **template_vars):
        """Write the makefile_usr.inc file which gets included in the main
        makefile by the ``makenek`` tool.

        Parameters
        ----------
        template : jinja2.environment.Template
            Template instance loaded from something like ``makefile_usr.inc.j2``
        fp : io.TextIOWrapper
            File handler to write to
        comments: str
            Comments on top of the box file
        template_vars: dict
            Keyword arguments passed while rendering the Jinja templates

        """

        paths_of_sources = []

        for path_dir, list_of_sources in self.makefile_usr_sources.items():
            for sources in list_of_sources:
                paths_of_sources.append([f"{path_dir}/{file}" for file in sources])

        if mpi.rank == 0:
            comments = "Autogenerated using snek5000.output.Output.write_makefile_usr\n"
            if self.sim is not None:
                comments += self.sim.params.short_name_type_run

            template_vars.update(
                {"list_of_sources": paths_of_sources, "comments": comments}
            )
            output = template.render(**template_vars)
            if fp:
                fp.write(output)
            else:
                makefile_usr = self.sim.path_run / "makefile_usr.inc"
                with open(makefile_usr, "w") as fp:
                    fp.write(output)

    def write_snakemake_config(self, custom_env_vars=None, host=None):
        """Write the config file in the simulation directory

        Parameters
        ----------
        custom_env_vars: dict (None)
            Environment variables used to update the configuration found by
            :meth:`find_configfile`.
        host: str
            Override hostname detection and specify it instead

        """
        if mpi.rank != 0:
            return

        path_configfile = self.find_configfile(host=host)
        path_configfile_simul = self.sim.path_run / self._config_filename

        with open(path_configfile) as file:
            config = yaml.safe_load(file)

        if custom_env_vars is None:
            shutil.copyfile(path_configfile, path_configfile_simul)
        else:
            config.update(custom_env_vars)
            with open(path_configfile_simul, "w") as file:
                yaml.dump(config, file)

        return config

    @staticmethod
    def build_nek5000(config):
        """Build Nek5000, if needed. This method is automatically invoked
        during :meth:`post_init`.

        Examples
        --------
        If compiler configuration is changed via a script after Simulation
        initialization, a rebuild can be manually triggered as follows:

        >>> config = sim.output.write_snakemake_config(
        ...     custom_env_vars={"CFLAGS": "-O0 -g", FFLAGS": "-O0 -g"}
        ... )
        >>> sim.output.build_nek5000(config)

        """
        nek5000 = _Nek5000Make()
        if not nek5000.build(config):
            raise RuntimeError("Nek5000 build failed.")

    @staticmethod
    def write_compile_sh(template, config, fp=None, path=None):
        """Write a standalone ``compile.sh`` shell script to compile the user
        code.

        Parameters
        ----------
        template: jinja2.environment.Template
            Template similar to ``snek5000/resources/compiler_sh.j2``
        config: dict
            Snakemake configuration
        fp: io.TextIOWrapper
            File pointer
        path: str or Path
            Path to write the file to

        """
        output = template.render(
            INC=config["includes"],
            USR=config["objects"],
            **config,
        )
        path = str(path)
        if fp:
            fp.write(output)
        elif path:
            with open(path, "w") as fp:
                fp.write(output)
        else:
            raise ValueError("Either file pointer or the path to it must be provided.")

        if path:
            os.chmod(path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)

    def get_field_file(self, prefix="", index=-1, t_approx=None):
        """Get a field file from ``path_session``.

        Parameters
        ----------
        prefix: str
            Prefix for special field files; for examples KTH statistics files use prefix `sts`.

        index: int
            Index to match a specific field file. If index > 0, the file
            extension is matched as ``{prefix}case0.f{index:05d}``. If index <
            0, the file is indexed from the end of a list of files

        t_approx: float
            Find a file from approximate simulation time

        Returns
        -------
        file: Path

        """
        case = self.name_solver
        path_session = self.sim.output.path_session

        if index > 0 and t_approx:
            raise ValueError("Specify either index or t_approx at a time, not both.")
        elif index > 0:
            pattern = f"{prefix}{case}0.f{index:05d}"
            file = path_session / pattern
            if file.exists():
                return file
            else:
                logger.warning(
                    f"{file} not found. Attempting to index a file from a "
                    "sorted list of field files"
                )
        elif t_approx:
            index = slice(None)

        pattern = f"{prefix}{case}0.f?????"
        try:
            result = sorted(path_session.glob(pattern))[index]
            if t_approx:
                result = bisect_nek_files_by_time(result, t_approx)

        except IndexError as err:
            raise FileNotFoundError(
                f"Cannot {index =} / find {t_approx =} in {path_session}/{pattern} "
            ) from err
        else:
            return result

    def post_init(self):
        """Logs info on instantiated classes and finally :meth:`copy` all
        source code to simulation directory

        """

        if mpi.rank == 0:
            print(f"path_run: {self.path_run}")
            logger.info(f"session_id: {self.params.session_id}")

        # This also calls _save_info_solver_params_xml
        with stdout_redirected():
            # We gather objects to print within Snek5000
            super().post_init()

        logger.info(self.sim._objects_to_print)

        # Write source files to compile the simulation
        if mpi.rank == 0 and self._has_to_save and self.sim.params.NEW_DIR_RESULTS:
            self.copy(self.path_run)
            config = self.write_snakemake_config()
            self.build_nek5000(config)
            self.post_init_create_additional_source_files()

    def post_init_create_additional_source_files(self):
        """Create the .box, SIZE and makefile_usr files from their template"""
        for name in ("box", "size", "makefile_usr"):
            try:
                template = getattr(self, f"template_{name}")
            except AttributeError:
                pass
            else:
                if template is not None:
                    getattr(self, f"write_{name}")(template)

    def _save_info_solver_params_xml(self, replace=False):
        """Saves the par file, along with ``params_simul.xml`` and
        ``info_solver.xml``"""
        params = self.sim.params
        if mpi.rank == 0:
            par_file = Path(self.path_run) / f"{self.name_solver}.par"

            if self._has_to_save and params.NEW_DIR_RESULTS:
                logger.info(
                    f"Writing params files... {par_file}, params_simul.xml, "
                    "info_solver.xml"
                )
                _save_par_file(params, par_file, mode="x")
            elif self._has_to_save:
                logger.info(f"Updating {par_file}, params_simul.xml")
                _save_par_file(params, par_file)

                # Update params_simul.xml here, since FluidSim Core will only
                # do it if NEW_DIR_RESULTS = True
                params_xml_path = self.path_run / "params_simul.xml"
                params_xml_path.unlink()
                comment = f"""\
This file should not be modified (except for adding xml comments).
Created by the Python programs:
snek5000 {__version__}
"""

                params._save_as_xml(path_file=params_xml_path, comment=comment)

        super()._save_info_solver_params_xml(replace, comment=f"snek5000 {__version__}")


Output.__doc__ += """
    Notes
    -----
    Here, only the documention for ``params.output`` is displayed.

    .. seealso::

        - ``params.oper`` at :mod:`snek5000.operators`
        - ``params.nek`` at :mod:`snek5000.solvers.base`

""" + docstring_params(
    Output
)
