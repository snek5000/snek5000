"""Load and parse spatial means data."""

from pathlib import Path

import pandas as pd


class SpatialMeans:
    INDEX_USERPARAM_SPATIAL_MEANS = 11
    _tag = "spatial_means"

    def __init__(self, output=None) -> None:
        self.output = output
        self.path_file = Path(output.path_run) / (self._tag + ".csv")

    @classmethod
    def _complete_params_with_default(cls, params):
        params.output._set_child(
            cls._tag,
            attribs={"write_interval": 1.0},
        )
        params.output.spatial_means._record_nek_user_params(
            {"write_interval": cls.INDEX_USERPARAM_SPATIAL_MEANS}
        )

    def load(self):
        return pd.read_csv(self.path_file)

    def plot(self, **kwargs):
        df = self.load()
        ax = df.plot("time", **kwargs)
        ax.figure.tight_layout()
