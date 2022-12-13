"""Load and parse stdout from Nek5000.

"""
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from fluiddyn.util.util import modification_date
from snek5000 import mpi

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
    def path_file(self):
        output = self.output
        if output and not self._path_file:
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
                self._path_file = path_run / f"{output.name_solver}.log"

        return self._path_file.resolve()

    @path_file.setter
    def path_file(self, path_log_file):
        self._path_file = path_log_file

    @property
    def text(self):
        with open(self.path_file) as fp:
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

    def __call__(self, *args):
        """Print to stdout and log file simultaneously."""
        mpi.printby0(*args)
        if mpi.rank == 0 and self.output._has_to_save:
            with self.path_file.open("a") as f:
                f.write(" ".join(str(a) for a in args) + "\n")

    def plot_dt_cfl(self):
        """Plot the evolution of the time step and the CFL number"""

        df = self.load()

        fig, (ax_top, ax_bot) = plt.subplots(nrows=2, sharex=True)

        ax_bot.plot(df.t, df.dt)
        ax_bot.set_title("time step")
        ax_bot.set_xlabel("time")

        ax_top.plot(df.t, df.CFL)
        ax_top.set_title("CFL number")

        params = self.output.sim.params

        if params.nek.general.variable_dt:
            ax_top.axhline(params.nek.general.target_cfl, color="r", label="Target CFL")
            ax_top.legend(loc="lower right")

        fig.tight_layout()

    def plot_nb_iterations(self):
        """Plot the evolution of the number of iterations for the Poisson solver"""

        df = self.load()

        fig, ax = plt.subplots()

        ax.plot(df.t, df.pres_it)
        ax.set_ylabel("number of iterations")
        ax.set_xlabel("time")

        fig.tight_layout()
