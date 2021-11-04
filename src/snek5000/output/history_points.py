from io import StringIO

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


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
        params.output.history_points._record_nek_user_params({"write_interval": 2})

    def load(self):
        with open(self.path_file) as file:
            line = file.readline()
            nb_points = int(line.split(" ", 1)[0])
            coords = np.loadtxt(file, max_rows=nb_points)
            lines = file.readlines()

        columns = ["time", "vx", "vy"]

        sim = self.output.sim
        if sim.params.oper.dim == 3:
            columns.append("vz")

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
            df = pd.read_fwf(StringIO("\n".join(lines)), header=None)
            df.columns = columns
        else:
            nb_times = 0
            df = pd.DataFrame({}, columns=columns)

        index_points = list(range(nb_points)) * nb_times
        df["index_points"] = index_points

        if sim.params.oper.dim == 2:
            columns = list("xy")
        else:
            columns = list("xyz")

        coords = pd.DataFrame(coords, columns=columns)

        return coords, df

    def plot(self, key="vx", data=None):
        if data is None:
            coords, df = self.load()
        else:
            coords, df = data

        fig, ax = plt.subplots()

        for index in range(self.nb_points):
            df_point = df[df.index_points == index]
            signal = df_point[key]
            times = df_point["time"]
            ax.plot(times, signal, label=str(tuple(coords.iloc[index])))

        ax.set_xlabel("time")
        ax.set_ylabel(key)
        fig.legend()
        fig.tight_layout()

        return ax
