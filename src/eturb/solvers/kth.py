from .base import SimulNek


class SimulKTH(SimulNek):
    """A base class which incorporates parameters for KTH toolbox also."""

    @staticmethod
    def _complete_params_with_default(params):
        params = SimulNek._complete_params_with_default(params)

        for section in ("runpar", "monitor", "chkpoint", "stat"):
            params.nek._set_child(section, {"_enabled": True})
            section_name_par = "_" + section.upper()
            params._par_file.add_section(section_name_par)

        attribs = {"parf_write": False, "parf_name": "outparfile"}
        params.nek.runpar._set_attribs(attribs)
        params.nek.runpar._set_doc(
            """
[_RUNPAR]               # Runtime parameter section for rprm module
PARFWRITE            = no                     # Do we write runtime parameter file
PARFNAME             = outparfile             # Runtime parameter file name for output (without .par)
"""
        )

        attribs = {"log_level": 4, "wall_time": "23:45"}
        params.nek.monitor._set_attribs(attribs)
        params.nek.monitor._set_doc(
            """
[_MONITOR]              # Runtime parameter section for monitor module
LOGLEVEL             = 4                      # Logging threshold for toolboxes
WALLTIME             = 23:45                  # Simulation wall time
"""
        )

        attribs = {"read_chkpt": False, "chkp_fnumber": 1, "chkp_interval": 250}
        params.nek.chkpoint._set_attribs(attribs)
        params.nek.chkpoint._set_doc(
            """
[_CHKPOINT]             # Runtime paramere section for checkpoint module
READCHKPT            = no                     # Restat from checkpoint
CHKPFNUMBER          = 1                      # Restart file number
CHKPINTERVAL         = 250                    # Checkpiont saving frequency (number of time steps)
"""
        )

        attribs = {"av_step": 4, "io_step": 50}
        params.nek.stat._set_attribs(attribs)
        params.nek.stat._set_doc(
            """
[_STAT]             # Runtime paramere section for statistics module
AVSTEP               = 10
IOSTEP               = 50

"""
        )
        return params
