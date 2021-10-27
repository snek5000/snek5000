from pathlib import Path


class HistoryPoints:
    """History points (Nek5000 output)

    See https://nek5000.github.io/NekDoc/problem_setup/features.html#history-points

    This is a very minimal (and buggy) implementation.

    """

    _tag = "history_points"

    def __init__(self, output=None):
        self.output = output
        sim = output.sim
        params = sim.params
        hp_params = params.output.history_points

        self.points = hp_params.points

        if self.points is None:
            return

        self.nb_points = len(self.points)

        self.path_file = (
            Path(output.path_run) / f"{sim.info_solver.short_name}.his"
        )
        if self.path_file.exists():
            return

        lines = [f"{self.nb_points} !number of monitoring points"]
        for xyz in self.points:
            lines.append(" ".join(str(value) for value in xyz))

        txt_hist = "\n".join(lines) + "\n"

        with open(self.path_file, "w") as file:
            file.write(txt_hist)

    @classmethod
    def _complete_params_with_default(cls, params):
        params.output._set_child(
            "history_points",
            attribs={"x": None, "y": None, "z": None, "points": None},
        )
