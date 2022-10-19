"""Interface for Nek5000 field files. :class:`PhysFields` usually
instantiated as ``sim.output.phys_fields`` provides a common interface for
plotting and reading arrays from the solution field files. Loading of data
files are managed by the classes in the :mod:`snek5000.output.readers`.

"""
from functools import lru_cache

import numpy as np
import matplotlib.pyplot as plt

import pymech
from pymech.neksuite.field import read_header

from fluiddyn.util import mpi

from fluidsim_core.params import iter_complete_params
from fluidsim_core.output.phys_fields import (
    SetOfPhysFieldFilesBase,
    PhysFieldsABC,
)
from fluidsim_core.output.movies import MoviesBasePhysFieldsHexa
from fluidsim_core.hexa_field import HexaField

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


class SetOfPhysFieldFiles(SetOfPhysFieldFilesBase):
    def _get_data_from_time(self, time):
        index = self.times.tolist().index(time)
        return self._get_data_from_path(self.path_files[index])

    @lru_cache(maxsize=2)
    def _get_data_from_path(self, path):
        return pymech.open_dataset(path)

    def _get_hexadata_from_time(self, time):
        index = self.times.tolist().index(time)
        return self._get_hexadata_from_path(self.path_files[index])

    @lru_cache(maxsize=2)
    def _get_hexadata_from_path(self, path):
        return pymech.readnek(path)

    def _get_field_to_plot_from_file(self, path_file, key, equation):
        if equation is not None:
            raise NotImplementedError
        hexa_data = self._get_hexadata_from_path(path_file)
        hexa_field = HexaField(key, hexa_data)
        return hexa_field, float(hexa_data.time)

    def init_hexa_pcolormesh(
        self, ax, hexa_color, hexa_x, hexa_y, vmin=None, vmax=None
    ):

        images = []

        if vmax is None:
            vmax = hexa_color.max()

        if vmin is None:
            vmin = hexa_color.min()

        for (arr, elem_x, elem_y) in zip(
            hexa_color.arrays, hexa_x.elements, hexa_y.elements
        ):

            x_edges = elem_x["edges"]
            y_edges = elem_y["edges"]

            image = ax.pcolormesh(
                x_edges, y_edges, arr, shading="flat", vmin=vmin, vmax=vmax
            )

            images.append(image)

        cbar = ax.figure.colorbar(images[0])

        return images, cbar

    def init_quiver_1st_step(self, hexa_x, hexa_y, percentage_dx_quiver=4.0):

        xmin = hexa_x.min()
        xmax = hexa_x.max()

        ymin = hexa_y.min()
        ymax = hexa_y.max()

        dx_quiver = percentage_dx_quiver / 100 * (xmax - xmin)
        nx_quiver = int((xmax - xmin) / dx_quiver)
        ny_quiver = int((ymax - ymin) / dx_quiver)

        x_approx_quiver = np.linspace(dx_quiver, xmax - dx_quiver, nx_quiver)
        y_approx_quiver = np.linspace(dx_quiver, ymax - dx_quiver, ny_quiver)

        indices_vectors_in_elems = []
        x_quiver = []
        y_quiver = []

        for x_2d, y_2d in zip(hexa_x.arrays, hexa_y.arrays):
            xmin = x_2d.min()
            xmax = x_2d.max()
            ymin = y_2d.min()
            ymax = y_2d.max()

            indices_vectors_in_elem = []

            for y_approx in y_approx_quiver:
                if y_approx < ymin:
                    continue
                if y_approx > ymax:
                    break
                for x_approx in x_approx_quiver:
                    if x_approx < xmin:
                        continue
                    if x_approx > xmax:
                        break

                    distance2_2d = (x_2d - x_approx) ** 2 + (y_2d - y_approx) ** 2

                    iy, ix = np.unravel_index(distance2_2d.argmin(), distance2_2d.shape)
                    indices_vectors_in_elem.append((iy, ix))

                    x_quiver.append(x_2d[iy, ix])
                    y_quiver.append(y_2d[iy, ix])

            indices_vectors_in_elems.append(indices_vectors_in_elem)

        return indices_vectors_in_elems, x_quiver, y_quiver

    def compute_vectors_quiver(self, hexa_vx, hexa_vy, indices_vectors_in_elems):
        vx_quiver = []
        vy_quiver = []
        vmax = -np.inf

        for indices_vectors_in_elem, arr_vx, arr_vy in zip(
            indices_vectors_in_elems, hexa_vx.arrays, hexa_vy.arrays
        ):

            vmax_elem = np.max(np.sqrt(arr_vx**2 + arr_vy**2))
            if vmax_elem > vmax:
                vmax = vmax_elem

            for iy, ix in indices_vectors_in_elem:
                vx_quiver.append(arr_vx[iy, ix])
                vy_quiver.append(arr_vy[iy, ix])

        return vx_quiver, vy_quiver, vmax

    def plot_hexa(
        self, time, equation="z=0", percentage_dx_quiver=4.0, vmin=None, vmax=None
    ):

        time = self.times[abs(self.times - time).argmin()]
        hexa_data = self._get_hexadata_from_time(time)

        key_field = self.get_key_field_to_plot()
        hexa_field = HexaField(key_field, hexa_data, equation=equation)
        hexa_x = HexaField("x", hexa_data, equation=equation)
        hexa_y = HexaField("y", hexa_data, equation=equation)
        hexa_vx = HexaField("vx", hexa_data, equation=equation)
        hexa_vy = HexaField("vy", hexa_data, equation=equation)

        fig, ax = plt.subplots()

        self.init_hexa_pcolormesh(ax, hexa_field, hexa_x, hexa_y, vmin=vmin, vmax=vmax)

        indices_vectors_in_elems, x_quiver, y_quiver = self.init_quiver_1st_step(
            hexa_x, hexa_y, percentage_dx_quiver=4.0
        )
        vx_quiver, vy_quiver, vmax = self.compute_vectors_quiver(
            hexa_vx, hexa_vy, indices_vectors_in_elems
        )
        ax.quiver(x_quiver, y_quiver, vx_quiver / vmax, vy_quiver / vmax)

        fig.tight_layout()

    def time_from_path(self, path):
        header = self.get_header(path)
        return header.time

    def get_header(self, path=None):
        if path is None:
            path = self.path_files[0]
        with open(path, "rb") as file:
            return read_header(file)

    def _get_glob_pattern(self):
        session_id = self.output.sim.params.output.session_id
        case = self.output.name_solver
        return f"session_{session_id:02d}/{case}0.f?????"

    def get_vector_for_plot(self, time, equation=None):
        if equation is not None:
            raise NotImplementedError
        # temporary hack
        time = self.times[abs(self.times - time).argmin()]
        hexa_data = self._get_hexadata_from_time(time)
        vec_xaxis = HexaField(hexa_data=hexa_data, key="vx")
        vec_yaxis = HexaField(hexa_data=hexa_data, key="vy")
        return vec_xaxis, vec_yaxis

    def get_key_field_to_plot(self, key_prefered=None):
        if key_prefered is None:
            header = self.get_header()
            if "T" in header.variables:
                return "temperature"
            return "pressure"
        else:
            return key_prefered
