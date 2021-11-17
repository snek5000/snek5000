import matplotlib.pyplot as plt

from snek5000.output.phys_fields import PhysFields
from snek5000.output.readers.pymech_ import ReaderPymech


class ReaderPymechAvg(ReaderPymech):
    """Horizontally and temporally averaged profiles."""

    tag = "pymech_avg"

    def load(self, prefix="", index="all", t_stat=None, **kwargs):
        ds = super().load(prefix, index, **kwargs)

        avg_dims = ("x", "z", "time")
        # Use xarray's sel method to slice along time and mean method to do the
        # averaging
        self.data = ds.sel(time=slice(t_stat, None)).mean(avg_dims)
        return self.data


class PhysFieldsCanonical(PhysFields):
    @staticmethod
    def _complete_info_solver(info_solver, classes=None):
        PhysFields._complete_info_solver(info_solver, classes=(ReaderPymechAvg,))

    def plot_mean_vel(self, marker="x"):
        """Plot mean velocity profiles against y-coordinate."""
        fix, ax = plt.subplots()
        data = self.data
        ax.plot("ux", "y", "", marker=marker, label="$U$", data=data)
        ax.plot("uy", "y", "", marker=marker, label="$V$", data=data)
        ax.plot("uz", "y", "", marker=marker, label="$W$", data=data)
        ax.set(ylabel="$y$")
        ax.legend()
