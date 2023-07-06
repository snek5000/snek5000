"""Interface for Nek5000 history points

"""
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from snek5000.util import repeat

INDEX_USERPARAM_HISTORY_POINTS = 10


class HistoryPoints:
    """History points (Nek5000 output)

    See https://nek5000.github.io/NekDoc/problem_setup/features.html#history-points

    """

    def __init__(self, output=None):
        self.output = output
        sim = output.sim
        params = sim.params
        hp_params = params.output.history_points

        self.coords = hp_params.coords

        if self.coords is None:
            return

        self.nb_points = len(self.coords)
        self.coords = np.array(self.coords)
        shape = self.coords.shape

        self._data = None

        if shape[0] >= params.oper.max.hist or shape[1] != params.oper.dim:
            raise ValueError(
                "Shape of params.output.history_points.coords are not compatible."
                f"Should be (< {params.oper.max.hist = }, == {params.oper.dim = })"
            )

        self.path_file = output.path_session / f"{sim.info_solver.short_name}.his"
        if self.path_file.exists() or not self.output._has_to_save:
            return

        # temporary?
        output.path_session.mkdir(exist_ok=True)

        with open(self.path_file, "w") as file:
            file.write(f"{self.nb_points} !number of monitoring coords\n")
            np.savetxt(file, self.coords, fmt="%.7E")

    @classmethod
    def _complete_params_with_default(cls, params):
        params.output._set_child(
            "history_points",
            attribs={"coords": None, "write_interval": 100},
        )
        params.output.history_points._record_nek_user_params(
            {"write_interval": INDEX_USERPARAM_HISTORY_POINTS}
        )
        params.output.history_points._set_doc(
            f"""
User parameter for history_points (subroutine hpts):

- ``coords``: list[tuple[float, float]] for 2D or list[tuple[float, float, float]] for 3D

   Coordinates of probes which gets written into the ``*.his`` file. Serves as input
   array for subroutine `hpts()` in Nek5000.

- ``write_interval``: int

   Interval to invoke `hpts()` subroutine. Gets recorded as user parameter number
   {INDEX_USERPARAM_HISTORY_POINTS}. This should be coupled within `userchk()` subroutine
   as follows:

   .. code-block:: fortran

      integer nit_hist

      nit_hist = abs(UPARAM(10))
      if (lhis.gt.1) then
          if (mod(ISTEP,nit_hist).eq.0) then
              call hpts()
          endif
      endif
"""
        )

    def load(self):
        if self.coords is None:
            raise ValueError(
                "No history points were defined in this simulation / solver."
            )
        elif self._data is None:
            return self._load_full()
        else:
            nb_points = self.coords.shape[0]
            nb_data_lines_read = len(self._data)

            size_file = self.path_file.stat().st_size

            with open(self.path_file) as file:
                first_line = file.readline()
                line_coord = file.readline()
                for _ in repeat(nb_points - 1):
                    file.readline()

                line_data = file.readline()

            nb_chars_read = (
                len(first_line)
                + nb_points * len(line_coord)
                + nb_data_lines_read * len(line_data)
            )
            nb_chars_not_read = size_file - nb_chars_read
            if nb_chars_not_read == 0:
                return self.coords, self._data

            with open(self.path_file) as file:
                file.seek(nb_chars_read)
                lines = file.readlines()

            df_more = self._create_df_from_lines(lines, nb_points)
            if len(df_more) > 0:
                self._data = pd.concat(
                    [self._data, df_more], ignore_index=True, sort=False
                )

            return self.coords, self._data

    def _load_full(self):
        with open(self.path_file) as file:
            nb_points = int(file.readline().split(" ", 1)[0])
            coords = np.loadtxt(file, max_rows=nb_points)
            lines = file.readlines()

        if coords.ndim == 1:
            coords = coords.reshape((1, coords.size))

        # ('x', 'y') or ('x', 'y', 'z')
        columns = tuple("xyz"[: self.output.sim.params.oper.dim])
        self.coords = pd.DataFrame(coords, columns=columns)

        df = self._create_df_from_lines(lines, nb_points)
        self._data = df

        return self.coords, df

    def _create_df_from_lines(self, lines, nb_points):
        columns = ["time", "ux", "uy"]

        sim = self.output.sim
        if sim.params.oper.dim == 3:
            columns.append("uz")

        columns.append("pressure")

        for key in ("temperature", "scalar01"):
            if key not in sim.info_solver.par_sections_disabled:
                columns.append(key)

        # we want to be able to load data during the simulation
        if lines:
            nb_numbers_per_line = len(lines[0])

            while len(lines[-1]) != nb_numbers_per_line:
                lines = lines[:-1]

            nb_times = len(lines) // nb_points
            lines = lines[: nb_times * nb_points]
            if lines:
                df = pd.read_fwf(StringIO("\n".join(lines)), header=None)
                df.columns = columns
            else:
                df = pd.DataFrame({}, columns=columns)
        else:
            nb_times = 0
            df = pd.DataFrame({}, columns=columns)

        index_points = list(range(nb_points)) * nb_times
        df["index_points"] = index_points

        return df

    def plot(self, key="ux"):
        coords, df = self.load()

        fig, ax = plt.subplots()

        for index in range(self.nb_points):
            df_point = df[df.index_points == index]
            signal = df_point[key]
            times = df_point["time"]
            ax.plot(times, signal, label=str(tuple(coords.iloc[index])))

        ax.set(xlabel="time", ylabel=key, title=self.output.summary_simul)
        fig.legend()
        fig.tight_layout()
        return ax

    def load_1point(self, index_point, key=None):
        coords, df = self.load()
        df_point = df[df.index_points == index_point]
        if key is not None:
            df_point = df_point[[key, "time"]]
        return coords, df_point

    def plot_1point(self, index_point, key, tmin=None, tmax=None):
        coords, df_point = self.load_1point(index_point, key)
        fig, ax = plt.subplots()

        signal = df_point[key]
        times = df_point["time"]

        if tmin is not None:
            signal = signal[times > tmin]
            times = times[times > tmin]

        if tmax is not None:
            signal = signal[times < tmax]
            times = times[times < tmax]

        ax.plot(times, signal)
        tmp = ", ".join("xyz"[: self.output.sim.params.oper.dim])
        ax.set(
            xlabel="time",
            ylabel=key,
            title=(
                self.output.summary_simul
                + f"\n{key}, ({tmp}) = {tuple(coords.values[index_point])}"
            ),
        )

        fig.tight_layout()
        return ax
