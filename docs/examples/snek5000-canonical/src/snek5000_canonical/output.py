from snek5000_canonical.templates import box, makefile_usr, size

from snek5000 import mpi
from snek5000.output.base import Output as OutputBase


class OutputCanonical(OutputBase):
    @classmethod
    def _set_info_solver_classes(cls, classes):
        """Set the the classes for info_solver.classes.Output

        NOTE: This method is optional, and only required if custom classes are
        to be set.

        """
        super()._set_info_solver_classes(classes)

        # Replace sim.output.phys_fields with a custom class
        classes.PhysFields.module_name = "snek5000_canonical.phys_fields"
        classes.PhysFields.class_name = "PhysFieldsCanonical"

    @property
    def makefile_usr_sources(self):
        """
        Sources for inclusion to makefile_usr.inc
        Dict[directory]  -> list of source files
        """
        return {}

        # For example this is the list of extra files required for the KTH
        # Framework:

        # return {
        #     "toolbox": [
        #         ("frame.f", "FRAMELP"),
        #         ("mntrlog_block.f", "MNTRLOGD"),
        #         ("mntrlog.f", "MNTRLOGD"),
        #         ("mntrtmr_block.f", "MNTRLOGD", "MNTRTMRD"),
        #         ("mntrtmr.f", "MNTRLOGD", "MNTRTMRD", "FRAMELP"),
        #         ("rprm_block.f", "RPRMD"),
        #         ("rprm.f", "RPRMD", "FRAMELP"),
        #         ("io_tools_block.f", "IOTOOLD"),
        #         ("io_tools.f", "IOTOOLD"),
        #         ("chkpoint.f", "CHKPOINTD"),
        #         ("chkpt_mstp.f", "CHKPTMSTPD", "CHKPOINTD"),
        #         ("map2D.f", "MAP2D", "FRAMELP"),
        #         ("stat.f", "STATD", "MAP2D", "FRAMELP"),
        #         ("stat_IO.f", "STATD", "MAP2D", "FRAMELP"),
        #         ("math_tools.f",),
        #     ],
        # }

    def post_init(self):
        super().post_init()

        # Write additional source files to compile the simulation
        if mpi.rank == 0 and self._has_to_save and self.sim.params.NEW_DIR_RESULTS:
            self.write_box(box)
            self.write_size(size)
            self.write_makefile_usr(makefile_usr)


Output = OutputCanonical
