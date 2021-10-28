from pathlib import Path

import numpy as np


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
