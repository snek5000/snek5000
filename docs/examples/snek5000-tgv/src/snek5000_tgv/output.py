from snek5000_tgv.templates import box, makefile_usr, size

from snek5000 import mpi
from snek5000.output.base import Output as OutputBase


class OutputTGV(OutputBase):
    @property
    def makefile_usr_sources(self):
        """
        Sources for inclusion to makefile_usr.inc
        Dict[directory]  -> list of source files
        """
        return {}

    def post_init(self):
        super().post_init()

        # Write additional source files to compile the simulation
        if mpi.rank == 0 and self._has_to_save and self.sim.params.NEW_DIR_RESULTS:
            self.write_box(box)
            self.write_size(size)
            self.write_makefile_usr(makefile_usr)

    @classmethod
    def _set_info_solver_classes(cls, classes):
        """Set the the classes for info_solver.classes.Output"""
        super()._set_info_solver_classes(classes)

        classes._set_child(
            "SpatialMeans",
            dict(
                module_name="snek5000.output.spatial_means",
                class_name="SpatialMeans",
            ),
        )


Output = OutputTGV
