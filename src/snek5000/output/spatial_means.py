"""Load and parse spatial means data."""

from .simple_csv import OutputWithCsvFileAndParam


class SpatialMeans(OutputWithCsvFileAndParam):
    INDEX_USERPARAM = 11
    _tag = "spatial_means"
    _param_name = "write_interval"
    _param_default_value = 1.0

    def plot(self, **kwargs):
        df = self.load()
        ax = df.plot("time", **kwargs)
        ax.figure.tight_layout()
