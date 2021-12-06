"""Load and parse stdout from Nek5000.

"""
import re
from datetime import datetime
from pathlib import Path
from warnings import warn

import pandas as pd

from fluiddyn.util.util import modification_date
from snek5000 import mpi
from snek5000.log import logger

# Uses awkupy
# %load_ext iawk


class PrintStdOut:
    """Parse standard output log files."""

    _tag = "print_stdout"

    def __init__(self, output=None, path_file=None):
        self.output = output
        self._path_file = path_file
        self.data = None
        self._data_modif_time = None

    @property
    def file(self):
        warn(
            "The property `file` is deprecated. Use `path_file` instead.",
            DeprecationWarning,
        )
        return self.path_file

    @property
    def path_file(self):
        output = self.output
        if output and not self._path_file:
            logger.info("Searching for a log file...")
            path_run = Path(output.path_run)
            logfiles = sorted(path_run.glob("*.log"))
            if logfiles:
                try:
                    self._path_file = next(
                        file
                        for file in logfiles
                        if file.name == f"{output.name_solver}.log"
                    )
                except StopIteration:
                    self._path_file = logfiles[-1]
            else:
                logger.info(f"Cannot find a .log to parse in {path_run}.")
                self._path_file = path_run / f"{output.name_solver}.log"

        return self._path_file.resolve()

    @path_file.setter
    def path_file(self, path_log_file):
        self._path_file = path_log_file

    @property
    def text(self):
        with open(self.file) as fp:
            return fp.read()

    def load(self, pressure_solver="gmres"):
        """Load time data from the log file"""
        # Parse text starting with Step
        # https://regex101.com/r/enFOAg/1

        path_file_time = modification_date(self.path_file)
        if self.data is not None and path_file_time <= self._data_modif_time:
            return self.data

        pattern_step = r"""^Step          # For all lines starting with Step
                \s*            # Followed by some whitespaces
                (?P<it>\d+)    # 0: Capture timestep which are integers
                .*             # Followed by some characters until
                t=\s*          # t=spaces
                (?P<t>\S+)     # 1: Capture t: any non-whitespace char
                ,\s*           # comma and spaces
                DT=\s*         # DT=spaces
                (?P<dt>\S+)    # 2: Capture DT: any non-whitespace char
                ,\s*           # comma and spaces
                C=\s*          # C=spaces
                (?P<CFL>\S+)   # 3: Capture C: any non-whitespace char
            """
        # TODO: add undocumented params.nek.pressure.solver parameter
        # See Line 445 in Nek5000/core/reader_par.f
        pattern_pressure = rf"""^\ +
                (?P<it2>\d+)
                .*
                PRES\ {pressure_solver}    # For all lines containing a string like PRES gmres
                \s+
                (?P<pres_it>\d+)
                \s+
                (?P<pres_div>\S+)
                \s+
                (?P<pres_div0>\S+)
                \s+
                (?P<pres_tol>\S+)
                \s+
                (?P<pres_etime>\S+)
                \s+
                (?P<pres_etime1>\S+)
            """

        expr = re.compile(
            f"({pattern_step})|({pattern_pressure})",
            re.VERBOSE | re.MULTILINE,
        )

        keys_all = tuple(expr.groupindex)
        # Divide into two tuples at "it2"
        idx = keys_all.index("it2")
        keys_step, keys_pressure = keys_all[:idx], keys_all[idx:]

        matches = tuple(expr.finditer(self.text))

        def make_dict(keys):
            return {key: [m[key] for m in matches] for key in keys}

        def make_df(keys):
            return (
                pd.DataFrame.from_dict(make_dict(keys))
                .dropna()
                .astype({key: int if key == "it" else float for key in keys})
            )

        df_step = make_df(keys_step).set_index("it")
        df_pressure = (
            make_df(keys_pressure).rename(columns={"it2": "it"}).set_index("it")
        )

        self.data = df_step.join(df_pressure)
        self._data_modif_time = path_file_time
        return self.data

    @property
    def dt(self):
        """Extract time step dt over the course of a simulation."""
        warn(
            "The property `dt` is deprecated. Use `load()` instead.", DeprecationWarning
        )
        return self.data.dt

    def estimate_clock_times(self):
        """Computed estimated walltime / clock time to complete the simulation
        and clock time per time step

        """
        last_data = self.load().tail(1)

        # FIXME: ctime is not creation time?
        first_timestamp = datetime.fromtimestamp(self.path_file.stat().st_ctime)
        last_timestamp = self._data_modif_time
        time_elapsed = last_timestamp - first_timestamp

        params = self.output.sim.params
        if params.nek.general.stop_at == "end_time":
            t_end = params.nek.general.end_time
            t_last = last_data.t.astype(float)
            walltime_end = time_elapsed * (t_end - t_last) / t_last
        elif params.nek.general.stop_at == "num_steps":
            it_end = params.nek.general.num_steps
            it_last = last_data.index.astype(int)
            walltime_end = time_elapsed * (it_end - it_last) / it_last
        else:
            raise ValueError("Unexpected value for params.nek.general.stop_at")

        walltime_per_it = time_elapsed / last_data.index.astype(int)

        return {
            "Clock time remaining": walltime_end,
            "Clock time per timestep": walltime_per_it,
        }

    def __call__(self, *args):
        """Print to stdout and log file simultaneously."""
        mpi.printby0(*args)
        if mpi.rank == 0 and self.output._has_to_save:
            with self.path_file.open("a") as f:
                f.write(" ".join(str(a) for a in args) + "\n")
