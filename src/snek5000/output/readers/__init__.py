"""Nek5000 field file readers (backend for :mod:`snek5000.output.phys_fields`)

.. autosummary::
   :toctree:

   pymech_

.. paraview_

"""
from abc import ABC, abstractmethod


class ReaderBase(ABC):
    """Abstract base class for defining the interface of all reader classes"""

    tag = NotImplemented

    @classmethod
    def _complete_params_with_default(cls, params):
        params.output.phys_fields.available_readers.append(cls.tag)

    def __init__(self, sim):
        self.sim = sim

    @abstractmethod
    def open(self, filename):
        """Opens field file into memory"""
        ...

    @abstractmethod
    def get(self, key):
        """Get an array"""
        ...
