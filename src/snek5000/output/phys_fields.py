"""Interface for Nek5000 field files.

.. todo:: Load field files and make various plots of statistics

"""
from functools import cached_property


class PhysFields:
    """Class for loading, plotting simulation files."""

    @classmethod
    def _complete_params_with_default(cls, params):
        params.output._set_child("phys_fields", attribs={"reader": "pymech"})

    def __init__(self, output=None):
        self.output = output

    @cached_property
    def reader(self):
        #  tag = self.params.phys_fields
        self.sim.info_solver.reader.classes
        #  reader_cls = ...
        #  reader_backend = ...
        #  return reader_backend

    def load(self):
        path = self.path_run
        if path.is_dir():
            path = next(path.glob("*.nek5000"))
