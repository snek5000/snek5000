"""Runtime parameters
=====================
Scripting interface for Nek5000 :ref:`parameter file <nek:case_files_par>`.

"""
from configparser import ConfigParser
from math import nan
from sys import stdout

from fluiddyn.util import import_class
from fluidsim.base.params import Parameters as _Parameters
from inflection import camelize, underscore

from .info import InfoSolverBase

literal_python2nek = {nan: "<real>", None: "none", True: "yes", False: "no"}
literal_nek2python = {v: k for k, v in literal_python2nek.items()}
literal_prune = ("<real>", "")


class Parameters(_Parameters):
    """Container for reading, modifying and writing par_ files.

    .. _par: https://nek5000.github.io/NekDoc/problem_setup/case_files.html#parameter-file-par

    :param tag: A string representing name of case files (for example: provide
                 ``"abl"`` for files like ``abl.usr, abl.par`` etc).


    .. automethod: _read_par

    """

    def __init__(self, *args, **kwargs):
        self._set_internal_attr("_par_file", ConfigParser())

        super().__init__(*args, **kwargs)

        # Like in Python Nek5000's par files are case insensitive.
        # However for consistency, case sensitivity is enforced:
        self._par_file.optionxform = str

    def _read_par(self, path=None):
        """Read par file into ``self.nek`` member."""
        if not path:
            path = self._tag + ".par"

        params_nek = self.nek
        self._par_file.read(path)

        for section in self._par_file.sections():
            params_section = getattr(params_nek, section.lower().lstrip('_'))

            for option, value in self._par_file.items(section):
                if value in literal_nek2python:
                    value = literal_nek2python[value]
                setattr(params_section, underscore(option), value)

    def _update_par_section(self, section_name, section_dict):
        """Updates a section of the ``par_file`` object from a dictionary."""
        par = self._par_file
        section_name_par = section_name.upper().lstrip("_")

        if section_name_par not in par.sections():
            par.add_section(section_name_par)
        for option, value in section_dict.items():
            if value in literal_python2nek:
                value = literal_python2nek[value]

            if value in literal_prune:
                continue

            # Make everything consistent where values refer to option names
            if option in ("stop_at", "write_control", "equation"):
                value = camelize(str(value), uppercase_first_letter=False)

            par.set(
                section_name_par,
                camelize(str(option), uppercase_first_letter=False),
                str(value),
            )

    def _sync_par(self):
        """Sync values in ``self.nek`` to ``self._par_file`` object."""
        par = self._par_file

        if hasattr(self, "nek"):
            for section_name in self.nek._tag_children:
                section_dict = getattr(self.nek, section_name)._make_dict_tree()

                section_name_par = section_name.upper()
                self._update_par_section(section_name_par, section_dict)

                enabled = par.getboolean(section_name_par, "_enabled")
                if enabled:
                    par.remove_option(section_name_par, "_enabled")
                else:
                    par.remove_section(section_name_par)

    def _write_par(self, path=stdout):
        """Write contents of ``self._par_file`` to file handler opened in disk
        or to stdout.

        """
        self._sync_par()
        if isinstance(path, str):
            with open(path, "w") as fp:
                self._par_file.write(fp)
        else:
            self._par_file.write(path)


def create_params(input_info_solver):
    """Create a Parameters instance from an InfoSolverBase instance."""
    if isinstance(input_info_solver, InfoSolverBase):
        info_solver = input_info_solver
    elif hasattr(input_info_solver, "Simul"):
        info_solver = input_info_solver.Simul.create_default_params()
    else:
        raise ValueError("Can not create params from input input_info_solver.")

    params = Parameters(tag="params")
    dict_classes = info_solver.import_classes()

    dict_classes["Solver"] = import_class(
        info_solver.module_name, info_solver.class_name
    )

    for Class in list(dict_classes.values()):
        if hasattr(Class, "_complete_params_with_default"):
            try:
                Class._complete_params_with_default(params)
            except TypeError:
                try:
                    Class._complete_params_with_default(params, info_solver)
                except TypeError as e:
                    e.args += ("for class: " + repr(Class),)
                    raise

    return params
