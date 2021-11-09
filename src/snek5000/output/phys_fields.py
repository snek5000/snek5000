"""Interface for Nek5000 field files. :class:`PhysFields` usually
instantiated as ``sim.output.phys_fields`` provides a common interface for
plotting and reading arrays from the solution field files. Loading of data
files are managed by the classes in the :mod:`snek5000.output.readers`.

"""
from functools import cached_property

from fluidsim_core.params import iter_complete_params

#  from .readers import try_paraview_ as pv
from .readers import pymech_ as pm


class PhysFields:
    """Class for loading, plotting simulation files."""

    @staticmethod
    def _complete_info_solver(info_solver, classes=None):
        """Static method to complete the ParamContainer info_solver.

        Parameters
        ----------

        info_solver : :class:`snek5000.info.InfoSolverMake`

        classes : iterable of classes

          If a class has the same tag of a default class, it replaces the
          default one (for example with the tag 'pymech').

        """
        classesXML = info_solver.classes.PhysFields._set_child("classes")

        avail_classes = [
            #  pv.ReaderParaview,
            #  pv.ReaderParaviewStats,
            pm.ReaderPymech,
            pm.ReaderPymechStats,
        ]
        if classes is not None:
            avail_classes.extend(classes)

        for cls in avail_classes:
            classesXML._set_child(
                cls.tag,
                attribs={
                    "module_name": cls.__module__,
                    "class_name": cls.__name__,
                },
            )

    @classmethod
    def _complete_params_with_default(cls, params, info_solver):
        params.output._set_child(
            "phys_fields", attribs={"reader": "pymech", "available_readers": []}
        )

        dict_classes = info_solver.classes.Output.classes.PhysFields.import_classes()
        iter_complete_params(params, info_solver, dict_classes.values())

    @cached_property
    def _reader(self):
        """An instance which implements :class:`snek5000.output.readers.ReaderBase`."""
        sim = self.output.sim

        reader_key = self.params.phys_fields.reader
        dict_classes = (
            sim.info.solver.classes.Output.classes.PhysFields.import_classes()
        )
        Class = dict_classes[reader_key]
        return Class(self.output)

    def __init__(self, output=None):
        self.output = output
        self.params = output.params
