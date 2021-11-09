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

    def __init__(self, output):
        self.output = output
        self.data = None

    @abstractmethod
    def load(self, prefix="", index=-1):
        """Opens field file and loads into memory as :attr:`data`"""
        ...

    @abstractmethod
    def get_var(self, key):
        """Get an array"""
        ...
