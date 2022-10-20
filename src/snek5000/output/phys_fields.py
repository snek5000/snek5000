"""Interface for Nek5000 field files. :class:`PhysFields` usually
instantiated as ``sim.output.phys_fields`` provides a common interface for
plotting and reading arrays from the solution field files. Loading of data
files are managed by the classes in the :mod:`snek5000.output.readers`.

"""
from functools import lru_cache

from fluidsim_core.params import iter_complete_params
from fluidsim_core.output.phys_fields import PhysFieldsABC
from fluidsim_core.output.movies import MoviesBasePhysFieldsHexa
from fluidsim_core.hexa_files import SetOfPhysFieldFiles

from ..log import logger

#  from .readers import try_paraview_ as pv
from .readers import pymech_ as pm


class PhysFields(PhysFieldsABC):
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
        classes_xml = info_solver.classes.PhysFields._set_child("classes")

        avail_classes = [
            #  pv.ReaderParaview,
            #  pv.ReaderParaviewStats,
            pm.ReaderPymech,
            pm.ReaderPymechStats,
        ]
        if classes is not None:
            avail_classes.extend(classes)

        for cls in avail_classes:
            classes_xml._set_child(
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

    @property
    def data(self):
        data = self._reader.data
        if not data:
            self.load()
            data = self._reader.data
        return data

    def __init__(self, output=None):
        self.output = output
        self.params = output.params

        self._reader = None  #: Reader instance

        self.load = self._uninitialized
        """Reader method which loads a particular file into memory and returns it.

        .. seealso::
            :meth:`snek5000.output.readers.ReaderBase.load`
        """

        self.get_var = self._uninitialized
        """Reader method which returns a particular array from memory.

        .. seealso::
            :meth:`snek5000.output.readers.ReaderBase.get_var`
        """

        self.set_of_phys_files = SetOfPhysFieldFiles(output=output)
        self.plot_hexa = self.set_of_phys_files.plot_hexa

        self.movies = MoviesBasePhysFieldsHexa(self.output, self)
        self.animate = self.movies.animate
        self.interact = self.movies.interact
        self._equation = None

    def _uninitialized(self, *args, **kwargs):
        """Place holder method to raise a :exc:`RuntimeError` while accessing
        :meth:`init_reader` not initialized.

        """
        raise RuntimeError(
            "The reader and the method has not initialized yet. "
            "Call sim.output.phys_fields.init_reader() to initialize the reader."
        )

    def init_reader(self):
        """Initializes the reader instance following the value in
        ``params.output.phys_fields.reader``. This would also "initialize"
        :meth:`load` and :meth:`get_var`.

        """
        if self._reader:
            logger.warning(
                "The reader is already initialized. Use change_reader() "
                "if you need to change the backend"
            )
            return

        reader_key = self.params.phys_fields.reader
        self.change_reader(reader_key)

    def change_reader(self, reader_key):
        """Changes the reader following which ``reader_key`` is provided.

        Parameters
        ----------
        reader_key: str
            String denoting the reader class. Should be one of
            ``params.output.phys_fields.available_readers``.

        """
        sim = self.output.sim

        dict_classes = (
            sim.info.solver.classes.Output.classes.PhysFields.import_classes()
        )
        try:
            cls = dict_classes[reader_key]
        except AttributeError as err:
            available_readers = self.params.phys_fields.available_readers
            raise ValueError(
                f"{reader_key =} not found in {available_readers =}"
            ) from err

        self._reader = cls(self.output)
        self.load = self._reader.load
        self.get_var = self._reader.get_var

    def get_key_field_to_plot(self, forbid_compute=False, key_prefered=None):
        return self.set_of_phys_files.get_key_field_to_plot(key_prefered)

    def get_field_to_plot(
        self,
        key=None,
        time=None,
        idx_time=None,
        equation=None,
        interpolate_time=True,
    ):
        """Get the field to be plotted in process 0."""
        return self.set_of_phys_files.get_field_to_plot(
            time=time,
            idx_time=idx_time,
            key=key,
            equation=equation,
            interpolate_time=interpolate_time,
        )

    def get_vector_for_plot(self, from_state=False, time=None, interpolate_time=True):
        if from_state:
            raise ValueError("cannot get anything from the state for this solver")
        return self.set_of_phys_files.get_vector_for_plot(time, self._equation)

    def _quiver_plot(self, ax, vecx, vecy, XX=None, YY=None):
        """Superimposes a quiver plot of velocity vectors with a given axis
        object corresponding to a 2D contour plot.
        """
        pass

    @lru_cache(maxsize=None)
    def _get_axis_data(self, equation=None):
        hexa_x, _ = self.get_field_to_plot(idx_time=0, key="x", equation=equation)
        hexa_y, _ = self.get_field_to_plot(idx_time=0, key="y", equation=equation)
        return hexa_x, hexa_y
