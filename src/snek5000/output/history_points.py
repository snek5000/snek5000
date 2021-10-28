from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class HistoryPoints:
    """History points (Nek5000 output)

    See https://nek5000.github.io/NekDoc/problem_setup/features.html#history-points

    This is a very minimal (and buggy) implementation.

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
                f"Should be (< {params.oper.max.hist}, == {params.oper.dim})"
            )

        self.path_file = (
            Path(output.path_run) / f"{sim.info_solver.short_name}.his"
        )
        if self.path_file.exists():
            return

        with open(self.path_file, "w") as file:
            file.write(f"{self.nb_points} !number of monitoring coords\n")
            np.savetxt(file, self.coords, fmt="%.7E")

    @classmethod
    def _complete_params_with_default(cls, params):
        params.output._set_child(
            "history_points",
            attribs={"coords": None},
        )

    def load(self):
        with open(self.path_file) as file:
            line = file.readline()
            nb_points = int(line.split(" ", 1)[0])
            coords = np.loadtxt(file, max_rows=nb_points)

        df = pd.read_fwf(self.path_file, skiprows=nb_points + 1, header=None)
        df.columns = list("tABDC")

        nb_times = len(df) // 25

        index_points = list(range(nb_points)) * nb_times
        df["index_points"] = index_points
        coords = pd.DataFrame(coords, columns=list("xy"))

        return coords, df

    def plot(self, key, data=None):
        if data is None:
            coords, df = self.load()
        else:
            coords, df = data

        fig, ax = plt.subplots()

        for index in range(self.nb_points):
            df_point = df[df.index_points == index]
            signal = df_point[key]
            times = df_point["t"]

            ax.plot(times, signal, label=str(tuple(coords.iloc[index])))

        ax.set_xlabel("time")
        fig.legend()

        return ax
