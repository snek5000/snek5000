"""Plot remaining clock time

"""

import numpy as np

from fluidsim_core.output.remaining_clock_time import RemainingClockTime as Base

from .simple_csv import OutputWithCsvFileAndParam


class RemainingClockTime(OutputWithCsvFileAndParam, Base):
    INDEX_USERPARAM = 12
    _tag = "remaining_clock_time"
    _param_name = "period_save_in_seconds"
    _param_default_value = 5.0

    def _load_times(self):
        df = self.load()
        data = {key: df[key].values for key in df.keys()}
        data["full_clock_time"] = np.nansum(data["delta_clock_times"])
        data["equation_time_start"] = df.loc[0, "equation_times"]
        return data

    def load(self):
        if not self.path_file.exists():
            raise IOError(
                f"No file {self.path_file}. "
                "Is it saved by a function in the .usr file? "
                "See https://github.com/snek5000/snek5000/blob/main/docs/examples/snek5000-tgv/src/snek5000_tgv/tgv.usr.f"
            )

        df = super().load()
        df["delta_equation_times"] = df.equation_times.diff()
        delta_time_inds = df.it.diff()
        df["clock_times_per_timestep"] = df["delta_clock_times"] / delta_time_inds
        keys = (
            "delta_clock_times",
            "delta_equation_times",
            "clock_times_per_timestep",
        )
        df.loc[df["it"] == 0, keys] = np.nan
        return df

    def plot(self):
        self.plot_clock_times()
