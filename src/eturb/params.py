"""Runtime parameters
=====================
Scripting interface for Nek5000 :ref:`parameter file <nek:case_files_par>`.

"""
from configparser import ConfigParser
from math import nan
from sys import stdout

from fluidsim.base.params import Parameters as _Parameters


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
            params_section = getattr(params_nek, section)
            for option, value in self._par_file.items(section):
                if value in literal_nek2python:
                    value = literal_nek2python[value]
                setattr(params_section, option, value)

    def _update_par_section(self, section_name, section_dict):
        """Updates a section of the ``par_file`` object."""
        par = self._par_file
        if section_name not in par.sections():
            par.add_section(section_name)
        for option, value in section_dict.items():
            if value in literal_python2nek:
                value = literal_python2nek[value]
            if value in literal_prune:
                continue
            par.set(section_name, str(option), str(value))

    def _sync_par(self):
        """Sync values in ``self.nek`` to ``self._par_file`` object."""
        par = self._par_file
        #  par.read_dict(self._make_dict_tree())
        for section_name in par.sections():
            section_dict = getattr(
                self.nek, section_name
            )._make_dict_tree()
            self._update_par_section(section_name, section_dict)
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
        if isinstance(path, str):
            with open(path, "w") as fp:
                self._par_file.write(fp)
        else:
            self._par_file.write(path)
