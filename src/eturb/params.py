from configparser import ConfigParser
from copy import deepcopy
from math import nan
from sys import stdout

from fluiddyn.util.paramcontainer import ParamContainer as _ParamContainer


literal_python2nek = {nan: "<real>", None: "none", True: "yes", False: "no"}
literal_nek2python = {v: k for k, v in literal_python2nek.items()}


class Parameters:
    """Scripting interface for Nek5000 parameter_ file.

    .. _parameter: https://nek5000.github.io/NekDoc/problem_setup/case_files.html#parameter-file-par

    """

    def __init__(self, case):
        self.case = case
        self.params = params = _ParamContainer(tag=case)
        self.par_file = ConfigParser()
        # Like in Python Nek5000's par files are case insensitive.
        # However for consistency, case sensitivity is enforced:
        self.par_file.optionxform = str

        for section in ("GENERAL", "PROBLEMTYPE", "VELOCITY", "PRESSURE"):
            params._set_child(section, {"_enabled": True})
            self.par_file.add_section(section)

        for section in (
            "MESH",
            "TEMPERATURE",
            "SCALAR01",
            "CVODE",
        ):
            params._set_child(section, {"_enabled": False})

        params._set_doc(
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
        params.GENERAL._set_attribs(
            dict(
                startFrom="",
                stopAt="numSteps",
                endTime=nan,
                numSteps=1,
                dt=nan,
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
        params.PROBLEMTYPE._set_attribs(
            dict(
                equation="incompNS",
                variableProperties=False,
                stressFormulation=False,
            )
        )
        common = dict(residualTol=nan, residualProj=False,)
        params.VELOCITY._set_attribs(common)
        params.PRESSURE._set_attribs(common)
        params.TEMPERATURE._set_attribs(common)
        params.SCALAR01._set_attribs(common)

        params.VELOCITY._set_attribs(dict(viscosity=nan, density=nan))
        params.PRESSURE._set_attrib("preconditioner", "semg_xxt")

    def read_par(self, path=None):
        """Read par file into params."""
        if not path:
            path = self.case + ".par"

        params = self.params
        self.par_file.read(path)

        for section in self.par_file.sections():
            params_section = getattr(params, section)
            for option, value in self.par_file.items(section):
                if value in literal_nek2python:
                    value = literal_nek2python[value]
                setattr(params_section, option, value)

    def sync_par(self):
        """Sync values in params to par object."""
        par = self.par_file
        #  par.read_dict(self.params._make_dict_tree())
        for section in par.sections():
            section_dict = getattr(self.params, section)._make_dict_tree()
            breakpoint()
            par[section].update(section_dict)
            enabled = par.getboolean(section, "_enabled")
            if enabled:
                par.remove_option(section, "_enabled")
            else:
                par.remove_section(section)

        for section in par.sections():
            for option, value in par.items(section):
                if value in literal_python2nek and value is not nan:
                    value = literal_python2nek[value]
                par.set(section, option, value)

    def write_par(self, path=stdout):
        self.sync_par()
        if isinstance(path, str):
            with open(path, "w") as fp:
                self.par_file.write(fp)
        else:
            self.par_file.write(path)
