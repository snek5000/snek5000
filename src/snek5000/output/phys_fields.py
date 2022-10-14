"""Interface for Nek5000 field files. :class:`PhysFields` usually
instantiated as ``sim.output.phys_fields`` provides a common interface for
plotting and reading arrays from the solution field files. Loading of data
files are managed by the classes in the :mod:`snek5000.output.readers`.

"""
from functools import lru_cache

import numpy as np

from fluiddyn.util import mpi

from fluidsim_core.params import iter_complete_params
from fluidsim_core.output.phys_fields import (
    SetOfPhysFieldFilesBase,
    PhysFieldsABC,
)
from fluidsim_core.output.movies import MoviesBasePhysFields

from ..log import logger

#  from .readers import try_paraview_ as pv
from .readers import pymech_ as pm

import pymech


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
        self.movies = MoviesBasePhysFields(self.output, self)
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
        return "temperature"

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
            time,
            idx_time=idx_time,
            key=key,
            equation=equation,
            interpolate_time=interpolate_time,
        )

    def get_vector_for_plot(self, from_state=False, time=None, interpolate_time=True):
        return self.set_of_phys_files.get_vector_for_plot(time, self._equation)

    def _quiver_plot(self, ax, vecx, vecy, XX=None, YY=None):
        """Superimposes a quiver plot of velocity vectors with a given axis
        object corresponding to a 2D contour plot.
        """

        if XX is None and YY is None:
            x_seq, y_seq = self._get_axis_data(self._equation)
            [XX, YY] = np.meshgrid(x_seq, y_seq)

        if mpi.rank == 0:
            vmax = np.max(np.sqrt(vecx**2 + vecy**2))

            if not hasattr(self, "_skip_quiver"):
                self._init_skip_quiver()

            skip = self._skip_quiver
            # copy to avoid a bug
            vecx_c = vecx[::skip, ::skip].copy()
            vecy_c = vecy[::skip, ::skip].copy()
            quiver = ax.quiver(
                XX[::skip, ::skip],
                YY[::skip, ::skip],
                vecx_c / vmax,
                vecy_c / vmax,
            )
        else:
            quiver = vmax = None

        return quiver, vmax

    @lru_cache(maxsize=None)
    def _get_axis_data(self, equation=None):
        data = self.data
        if equation is not None:
            raise NotImplementedError
        return data.x.data, data.y.data


class SetOfPhysFieldFiles(SetOfPhysFieldFilesBase):
    def _get_data_from_time(self, time):
        index = self.times.tolist().index(time)
        return self._get_data_from_path(self.path_files[index])

    @lru_cache(maxsize=2)
    def _get_data_from_path(self, path):
        return pymech.open_dataset(path)

    def _get_field_to_plot_from_file(self, path_file, key, equation):
        data = self._get_data_from_path(path_file)
        field = data[key].data
        if equation is not None:
            raise NotImplementedError
        return field[0], float(data.time)

    @staticmethod
    def time_from_path(path):
        return pymech.readnek(path).time

    def _get_glob_pattern(self):
        session_id = self.output.sim.params.output.session_id
        case = self.output.name_solver
        return f"session_{session_id:02d}/{case}0.f?????"

    def get_vector_for_plot(self, time, equation=None):

        if equation is not None:
            raise NotImplementedError

        # temporary hack
        time = self.times[abs(self.times - time).argmin()]

        data = self._get_data_from_time(time)

        vec_xaxis = data["ux"].data[0]
        vec_yaxis = data["uy"].data[0]
        return vec_xaxis, vec_yaxis
