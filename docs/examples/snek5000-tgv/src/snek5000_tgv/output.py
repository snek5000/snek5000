from snek5000.output.base import Output as OutputBase
from snek5000.resources import get_base_templates

box, makefile_usr, size = get_base_templates()


class OutputTGV(OutputBase):
    template_box = box
    template_makefile_usr = makefile_usr
    template_size = size

    @property
    def makefile_usr_sources(self):
        """
        Sources for inclusion to makefile_usr.inc
        Dict[directory]  -> list of source files
        """
        return {}

    @classmethod
    def _set_info_solver_classes(cls, classes):
        """Set the classes for info_solver.classes.Output"""
        super()._set_info_solver_classes(classes)

        classes._set_child(
            "SpatialMeans",
            dict(
                module_name="snek5000.output.spatial_means",
                class_name="SpatialMeans",
            ),
        )


Output = OutputTGV
