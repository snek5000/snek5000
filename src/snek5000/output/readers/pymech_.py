"""Read field files using ``pymech`` as ``xarray`` datasets."""

import pymech as pm

from ...log import logger
from . import ReaderBase


class ReaderPymech(ReaderBase):
    tag = "pymech"

    def load(self, prefix="", index=-1, t_approx=None, **kwargs):
        """Opens field files(s) as a xarray dataset. The data is cached in
        :attr:`data`.

        Parameters
        ----------
        prefix: str
            Field file prefix to load custom output files. Empty for default
            field files.

        index : int or str
            When an integer is provided, it refers to the index position in a
            sorted list of field files. When ``index == "all"`` all files are
            loaded. When ``index`` is some other string, it is assumed to be
            glob pattern for the final 5 digits of the field filename extension
            (for example: ``"??20?"``).

        t_approx: float
            Find a file from approximate simulation time

        **kwargs
            Keyword arguments for ``pymech.open_*`` function

        Returns
        -------
        ds: xarray.Dataset

        """
        if isinstance(index, int):
            path_file = self.output.get_field_file(prefix, index, t_approx)
            ds = pm.open_dataset(path_file, **kwargs)
        elif isinstance(index, str):
            case = self.output.name_solver
            path = self.output.path_session
            ext = "?????" if index == "all" else index

            pattern = f"{prefix}{case}0.f{ext}"
            ds = pm.open_mfdataset(path.glob(pattern), **kwargs)
        else:
            raise ValueError("Parameter index should be int or str")

        self.data = ds
        return ds

    def get_var(self, key):
        """Return a specific array.

        Parameters
        ----------
        key: str
            Key indicating a DataArray in the loaded dataset stored in :attr:`data`.
            Must be called after :meth:`load`.

        Returns
        -------
        xarray.DataArray

        """
        if not self.data:
            logger.info("Using defaults of the load() method to read the data.")
            self.load()

        return self.data[key]


class ReaderPymechStats(ReaderPymech):
    tag = "pymech_stats"

    def load(self, prefix="sts", index=-1, **kwargs):
        """Opens statistics_ field files(s) as a xarray dataset

        .. _statistics: https://kth-nek5000.github.io/KTH_Framework/group__stat.html

        """
        return super().load(prefix, index, **kwargs)
