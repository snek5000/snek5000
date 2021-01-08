"""Runtime parameters
=====================
Scripting interface for Nek5000 :ref:`parameter file <nek:case_files_par>`.

"""
import textwrap
from configparser import ConfigParser
from io import StringIO
from math import nan
from pathlib import Path
from sys import stdout
from warnings import warn

from fluidsim_core.params import Parameters as _Parameters
from inflection import camelize, underscore

literal_python2nek = {
    nan: "<real>",
    "nan": "nan",
    "None": "none",
    "True": "yes",
    "False": "no",
}
literal_nek2python = {v: k for k, v in literal_python2nek.items()}
literal_prune = ("<real>", "", "nan")


def camelcase(value):
    return camelize(str(value).lower(), uppercase_first_letter=False)


def _check_user_param(idx):
    if idx > 20:
        raise ValueError(f"userParam {idx} > 20")


class Parameters(_Parameters):
    """Container for reading, modifying and writing par_ files.

    .. _par: https://nek5000.github.io/NekDoc/problem_setup/case_files.html#parameter-file-par

    :param tag: A string representing name of case files (for example: provide
                 ``"abl"`` for files like ``abl.usr, abl.par`` etc).

    .. automethod: _read_par


    :todo: Consolidate the logic of param to par file syncing in two methods!
           More tests to see if it works.

    """

    def __init__(self, *args, **kwargs):
        comments = ("#",)
        self._set_internal_attr(
            "_par_file",
            ConfigParser(comment_prefixes=comments, inline_comment_prefixes=comments),
        )
        # Only enabled parameters would be written into par file
        self._set_internal_attr("_enabled", True)
        # User parameters sections should begin with an underscore
        self._set_internal_attr("_user", True)

        if "path_file" in kwargs:
            warn(
                "Loading directly from path_file is an experimental feature. Use "
                "Simul.load_params_from_file() instead."
            )

        super().__init__(*args, **kwargs)

        # Like in Python Nek5000's par files are case insensitive.
        # However for consistency, case sensitivity is enforced:
        self._par_file.optionxform = str

    def _make_dict_attribs(self):
        d = super()._make_dict_attribs()
        # Append internal attributes
        d.update({"_enabled": self._enabled, "_user": self._user})
        return d

    def _read_par(self, path=None):
        """Read par file into a class children and attributes."""
        if not path:
            path = self._tag + ".par"

        self._par_file.read(path)

        for section in self._par_file.sections():
            params_child = getattr(self, section.lower().lstrip("_"))

            for option, value in self._par_file.items(section):
                if value in literal_nek2python:
                    value = literal_nek2python[value]

                # userParam%% -> user_params
                if option.lower().startswith("userparam"):
                    idx_uparam = int(option[-2:])
                    _check_user_param(idx_uparam)
                    params_child.user_params.update({idx_uparam: float(value)})
                else:
                    attrib = underscore(option)
                    setattr(params_child, attrib, value)

    def _update_par_section(self, section_name, section_dict):
        """Updates a section of the ``par_file`` object from a dictionary."""
        par = self._par_file

        # Start with underscore if it is a user section
        section_name_par = "_" if section_dict["_user"] else ""
        section_name_par += section_name.upper().lstrip("_")

        if section_name_par not in par.sections():
            par.add_section(section_name_par)
        for option, value in section_dict.items():
            # Convert to string to avoid hash collisions
            # hash(1) == hash(True)
            literal = str(value) if value is not nan else nan
            if literal in literal_python2nek:
                value = literal_python2nek[literal]

            if value in literal_prune:
                continue

            # Make everything consistent where values refer to option names
            # if option in ("stop_at", "write_control"):
            if str(value) in section_dict:
                value = camelcase(value)

            # user_params -> userParam%%
            if option.lower().startswith("user_params") and isinstance(value, dict):
                for idx_uparam, value_uparam in value.items():
                    _check_user_param(idx_uparam)
                    par.set(
                        section_name_par,
                        f"userParam{idx_uparam:02d}",
                        str(value_uparam),
                    )
            else:
                par.set(section_name_par, camelcase(option), str(value))

    def _sync_par(self):
        """Sync values in param children and attributes to ``self._par_file``
        object.

        """
        if self._tag_children:
            data = [
                (child, getattr(self, child)._make_dict_tree())
                for child in self._tag_children
            ]
        else:
            # No children
            data = [(self._tag, self._make_dict_attribs())]

        for child, d in data:
            section_name = child.upper()
            self._update_par_section(section_name, d)

        self._tidy_par()

    def _tidy_par(self):
        """Remove internal attributes and disabled sections from par file."""
        par = self._par_file
        for section_name in par.sections():
            par.remove_option(section_name, "_user")

            enabled = par.getboolean(section_name, "_enabled")
            if enabled:
                par.remove_option(section_name, "_enabled")
            else:
                par.remove_section(section_name)

    def _write_par(self, path=stdout):
        """Write contents of ``self._par_file`` to file handler opened in disk
        or to stdout.

        """
        self._sync_par()
        if isinstance(path, (str, Path)):
            with open(path, "w") as fp:
                self._par_file.write(fp)
        else:
            self._par_file.write(path)

    def _autodoc_par(self, indent=0):
        """Autodoc a code block with ``ini`` syntax and set docstring."""
        self._sync_par()
        docstring = "\n.. code-block:: ini\n\n"
        with StringIO() as output:
            self._par_file.write(output)
            ini = output.getvalue()

        docstring += textwrap.indent(ini, "   ")

        if ini:
            self._set_doc(self._doc + textwrap.indent(docstring, " " * indent))


create_params = Parameters._create_params
