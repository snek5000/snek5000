"""Paraview interface for Nek5000 files.

.. todo:: Load field files and make various plots of statistics

"""
from ..log import logger

try:
    import paraview.simple as pvs
    from paraview.simple import VisItNek5000Reader
except ImportError as e:
    logger.warning(e)

#  from vtktools import vtkio


class PhysFields:
    """Class for loading, plotting simulation files.

    :param sim: A simulation instance derived from
                :class:`snek5000.solvers.base.SimulNek`
    :param path: :class:`pathlib.Path` Path where simulation state files are
                 found.


    """

    def __init__(self, sim=None, path=None):
        self.sim = sim
        if not path and sim:
            self.path_run = sim.output.path_run
        else:
            self.path_run = path

    def read(self):
        path = self.path_run
        if path.is_dir():
            path = next(path.glob("*.nek5000"))

        # TODO: needed or not?
        # pvs._DisableFirstRenderCameraReset()
        self.reader = reader = VisItNek5000Reader(FileName=str(path))
        if not reader:
            raise IOError("Error while loading file " + path)

        reader.Meshes = ["mesh"]
        # get animation scene
        self.animationScene = pvs.GetAnimationScene()

        # get the time-keeper
        self.timeKeeper = pvs.GetTimeKeeper()

    def set_point_arrays(self, arrays=("velocity",)):
        self.reader.PointArrays = list(arrays)

    def contourf_paraview(self, array):
        assert array in self.reader.PointArrays
        renderView = pvs.GetActiveViewOrCreate("RenderView")

        # get color transfer function/color map for 'array'
        LUT = pvs.GetOpacityTransferFunction(array)

        # get color legend/bar for LUT in view renderView
        LUTColorBar = pvs.GetScalarBar(LUT, renderView)
        return renderView, LUTColorBar

    def set_time(self, time):
        self.animationScene.AnimationTime = time
        self.timeKeeper.Time = time
