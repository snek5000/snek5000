from functools import cached_property
from pathlib import Path

import numpy as np

from ...log import logger
from . import ReaderBase

try:
    import paraview.simple as pv
    from paraview.simple import *  # noqa: F401, F403
except ImportError:
    logger.debug("Paraview Python module cannot be imported")
else:
    # Continue importing VTK
    from vtk.numpy_interface import dataset_adapter as dsa  # algorithms as algs,
    from vtk.util.numpy_support import vtk_to_numpy


#  import pyvista
# from vtktools import vtkio


# disable automatic camera reset on 'Show'
# pv._DisableFirstRenderCameraReset()


class ReaderParaview(ReaderBase):
    """A user-friendly API for Paraview scripting with 'VisItNek5000Reader'."""

    tag = "paraview"

    def open(
        self,
        filename,  # <case>.nek5000
        arrays=(
            "pressure",
            "velocity_mag",
            "x_velocity",
            "y_velocity",
            "z_velocity",
        ),
    ):
        self.filename = filename
        assert Path(filename).exists()

        self.nek5000 = nek5000 = pv.VisItNek5000Reader(FileName=str(filename))
        nek5000.Meshes = ["mesh"]

        # get animation scene
        self.animationScene1 = pv.GetAnimationScene()

        # get the time-keeper
        self.timeKeeper1 = pv.GetTimeKeeper()

        # update animation scene based on data timesteps
        self.animationScene1.UpdateAnimationUsingDataTimeSteps()

        # Properties modified on ablnek5000
        assert isinstance(arrays, (list, tuple))
        nek5000.PointArrays = list(arrays)

        data_info = nek5000.GetDataInformation()
        self.dtype = data_info.GetDataSetTypeAsString()

    def __iter__(self):
        return self

    def __next__(self):
        """Iterate through time"""
        if self.time == self.animationScene1.EndTime:
            raise StopIteration

        self.animationScene1.GoToNext()
        self.animationScene1.AnimationTime = self.time

        #  self.animationScene1.UpdateAnimationUsingDataTimeSteps = self.time
        #  pv.UpdatePipeline(self.time)
        self.apply()

        # Return lightweight metadata as a tuple
        return (self.time,)

    @property
    def time(self):
        return self.timeKeeper1.Time

    @time.setter
    def time(self, value):
        """Seek a new time step and update pipeline."""
        # Properties modified on animationScene1
        self.animationScene1.AnimationTime = value
        # Properties modified on timeKeeper1
        self.timeKeeper1.Time = value
        self.apply()

    @property
    def timesteps(self):
        return self.timeKeeper1.TimestepValues

    @cached_property
    def renderView1(self):
        """Get active view."""
        return pv.GetActiveViewOrCreate("RenderView")

    @cached_property
    def temporalStatistics1(self):
        temporalStatistics1 = pv.TemporalStatistics(Input=self.nek5000)

        # Properties modified on temporalStatistics1
        temporalStatistics1.ComputeAverage = 1
        temporalStatistics1.ComputeMinimum = 0
        temporalStatistics1.ComputeMaximum = 0
        return temporalStatistics1

    @cached_property
    def groupDatasets1(self):
        return pv.GroupDatasets(Input=[self.temporalStatistics1, self.nek5000])

    @cached_property
    def bounds(self, source=None):
        Input = source if source else self.nek5000
        bounds = Input.GetDataInformation().GetBounds()
        if 1.0e299 in bounds:
            self.apply()
            bounds = Input.GetDataInformation().GetBounds()
        return bounds

    def show(self, key_array="x_velocity", source=None, rescale=False):
        """Show the rendered output on the screen."""
        Input = source if source else self.nek5000

        display = pv.Show(Input, self.renderView1)
        pv.ColorBy(display, ("POINTS", key_array))
        if rescale:
            display.RescaleTransferFunctionToDataRange(True, False)
        display.SetScalarBarVisibility(source, True)

        # ... lot of parameters are possible here

        pv.SetActiveSource(source)

        try:
            LUT = pv.GetColorTransferFunction(key_array)
            PWF = pv.GetOpacityTransferFunction(key_array)
        except AttributeError:
            LUT = PWF = None

        return display, LUT, PWF

    def apply(self):
        """Update pipeline with current timestep."""
        pv.UpdatePipeline(self.time)

    def render(self):
        renderView1 = self.renderView1
        renderView1.ResetCamera()
        renderView1.Update()

    def get_slice(self, x=0.0, y=0.0, z=0.0, normal=(0, 1, 0), source=None):
        slice1 = self.slice1 = pv.Slice(Input=source if source else self.nek5000)
        slice1.SliceType = "Plane"
        slice1.SliceOffsetValues = [0.0]
        slice1.SliceType.Origin = [x, y, z]
        slice1.SliceType.Normal = list(normal)
        # slice1.Triangulatetheslice = 0

        # slice_data = vtkio.getBlockByName(mb_dset, 'mesh')

        # pv.SetActiveSource(slice1)

        return _ParaviewSlice(slice1)
        # return pyvista.wrap(dobj)


class ReaderParaviewStats(ReaderParaview):
    tag = "paraview_stats"

    def open(
        self,
        filename,  # "sts<case>.nek5000",
        arrays=tuple(f"s{idx}" for idx in range(1, 45)),
    ):
        super().__init__(filename, arrays)

    def calculate(self, name="u_prime", func="s1_average - s1"):
        calculator1 = pv.Calculator(Input=self.groupDatasets1)
        calculator1.ResultArrayName = name
        calculator1.Function = func
        return calculator1


class _ParaviewSlice:
    """Convenience wrapper to easily access arrays stored in a VTK dataset."""

    def __init__(self, slice1):
        self._slice = slice1
        # vtkCommonDataModelPython.vtkMultiBlockDataSet
        dset = pv.servermanager.Fetch(slice1)

        if dset.GetClassName() not in ("vtkMultiBlockDataSet",):
            raise ValueError(f"Incompatible type: {type(dset)}")

        # <vtk.numpy_interface.dataset_adapter.CompositeDataSet
        self._dset = dset
        self._obj = dsa.WrapDataObject(dset)
        self._ptdata = self._obj.GetPointData()

    def __getitem__(self, key):
        keys = self.keys()

        if key in self._ptdata.keys():
            return self._ptdata.GetArray(key)
        elif key == "coords":
            return self._obj.Points
        else:
            raise KeyError(f"Valid keys are: {keys}")

    def keys(self):
        return ["coords"] + self._ptdata.keys()

    def get_blocks(self):
        nb_blocks = self._dset.GetNumberOfBlocks()
        return (self._dset.GetBlock(idx) for idx in range(nb_blocks))

    def get_array(self, key):
        vtk_array = self[key].Arrays[0]
        array = vtk_to_numpy(vtk_array)
        return array

    def get_coords(self, normal=1, sort=True, reshape=True):
        """Get row major sorted and reshaped coordinates for a slice.

        :param int normal: Axis normal to the slice
        :param bool sort: Sort the coordinate array or not
        :param bool reshape: Reshape the coordinates into 2D array or not.

        """
        coords = self.get_array("coords")
        # Remove normal directions
        axes = {0, 1, 2} - {normal}
        ax0, ax1 = sorted(axes)

        def sorting_indices(pts):
            """Sorts indices using a weighting function."""
            pts = np.copy(pts)

            # weighting_func = lambda x0, x1: x0 + x1 * 1e4
            # inds = np.argsort(weighting_func(pts[:, ax0], pts[:, ax1]))
            inds = np.lexsort([pts[:, ax] for ax in range(3)])
            return inds

        if sort:
            inds = sorting_indices(coords)
            coords = coords[inds]
        else:
            inds = None

        # Sorting coordinates
        def get_n0_n1(pts):
            """Estimate array shape"""
            # Look where index jumps occur
            # ----------------------------
            # For example 0, 1, 2, 3, (jump!) 0, 1, 2, 3
            inds_jumps = np.where(pts[:-1, ax0] > pts[1:, ax0])[0]
            # print(inds_jumps)
            n1 = inds_jumps[1] - inds_jumps[0]
            n1_avg = np.diff(inds_jumps).mean()
            assert (
                n1 == n1_avg
            ), f"{n1}!={n1_avg}, i.e. inhomogenieties found, reshaping may not be possible"

            n1 = int(n1)

            n0 = pts.shape[0] / n1
            assert n0.is_integer()
            n0 = int(n0)

            return n0 + 1, n1

        x, y, z = coords.T
        if reshape:
            n0, n1 = get_n0_n1(coords)
            axes = [self.reshape(ax, shape=(n0, n1)) for ax in (x, y, z)]
            return (*axes, inds)
        else:
            return x, y, z, inds

    def reshape(self, arr, shape):
        """Reshape 1D arrays into 2D arrays while also handling boundaries.

        :param arr: Array to be reshaped
        :param tuple(int) shape: Shape of the output array


        """
        n0, n1 = shape
        n0 -= 2
        n_bound = n1 // 2
        inner = arr[n_bound:-n_bound].reshape(n0, n1)

        def repeat(values):
            """Repeat an array like [0, 1, 2] -> [0, 0, 1, 1, 2, 2]"""
            n = values.size * 2
            values2 = np.empty((1, n), dtype=values.dtype)
            values2[0, ::2] = values
            values2[0, 1::2] = values
            return values2

        left_boundary = repeat(arr[:n_bound])
        right_boundary = repeat(arr[-n_bound:])

        return np.vstack((left_boundary, inner, right_boundary))

    def plot_contours(self, key, normal=1, interpolate=True, ax=None, **kwargs):
        # No sorting and reshaping is required if interpolation is allowed
        sort_reshape = not interpolate
        x, y, z, inds = self.get_coords(normal, sort_reshape, sort_reshape)
        field = self.get_array(key)

        import matplotlib.pyplot as plt

        if not ax:
            ax = plt

        if normal == 0:
            x0, x1 = y, z
        elif normal == 1:
            x0, x1 = x, z
        elif normal == 2:
            x0, x1 = x, y

        if interpolate:
            ax.tricontourf(x0, x1, field, **kwargs)
        else:
            #  field = field[inds].reshape(x0.shape)
            field = self.reshape(field[inds], shape=x0.shape)
            # print(field.shape, x0.shape)
            ax.contourf(x0, x1, field, **kwargs)


if __name__ in ("__main__", "__vtkconsole__"):
    pv._DisableFirstRenderCameraReset()
    reader = ReaderParaview(
        filename="abl.nek5000",
        arrays=("velocity", "velocity_mag"),
    )

    print(reader.time)
    # next(reader)

    # reader.render()
    #  for (time,) in reader:
    #      # reader.show("velocity_mag")
    #      print(time)
    #      break

    # reader.render()
    slice_data = reader.get_slice(y=0.1)

    velocity_mag = slice_data.get_array("velocity_mag")
    print(velocity_mag, velocity_mag.shape)
    coords = slice_data.get_array("coords")
    print(coords, coords.shape)
    x, y, z = coords.T
    print(x.shape)

    import matplotlib.pyplot as plt

    renderView1 = reader.renderView1
    renderView1.CameraPosition = [
        1.5430590649448526,
        6.463304979594418,
        4.555389168383411,
    ]
    renderView1.CameraFocalPoint = [1.5707999467849734, 0.5, 0.7853999733924866]
    renderView1.CameraViewUp = [
        0.018053943395482774,
        0.5343398685402572,
        -0.8450768959190954,
    ]
    renderView1.CameraParallelScale = 1.8259971497854517

    # plt.ion()
    reader.time = reader.timesteps[-5]
    fig, axes = plt.subplots(2, sharex=True)
    ax1, ax2 = axes.ravel()
    for (ts,) in reader:
        print("time =", ts)
        # renderView1.Update()
        slice_data = reader.get_slice(y=0.1)

        ax1.set_title("interpolated")
        slice_data.plot_contours("velocity_mag", interpolate=True, ax=ax1)
        ax2.set_title(f"actual, time={ts}")
        plt.title(f"time={ts}")
        slice_data.plot_contours("velocity_mag", interpolate=False, ax=ax2)

        # NOTE: Very important to execute reader.show / pv.Show, without which the animation
        # scene is not updated.
        display = reader.show("velocity_mag", slice_data._slice)
        # display = pv.Show(slice_data._slice, renderView1)
        # pv.ColorBy(display, ('POINTS', "velocity_mag"))

        # reader.render()
        # reader.apply()
        plt.pause(0.2)

    plt.pause(1.0)
