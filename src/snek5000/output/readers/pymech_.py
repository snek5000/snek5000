"""Read field files using ``pymech`` as ``xarray`` datasets."""

import pymech as pm

from . import ReaderBase


class ReaderPymech(ReaderBase):
    tag = "pymech"

    def open(self, prefix="", index=-1, **kwargs):
        """Opens field files(s) as a xarray dataset. The data is cached in
        :attr:`data`.

        Parameters
        ----------
        prefix: str
            Field file prefix to load custom output files. Empty for default
            field files.

        index : int or str
            When an integer is provided, it refers to the index posiion in a
            sorted list of field files. When a string is provided and the value
            is `all` it loads all files, if not the value is assumed to be glob
            pattern for the final 5 digits of the field filename extension (for
            example: ``??20?``).

        **kwargs
            Keyword arguments for ``pymech.open_*`` function

        Returns
        -------
        ds: xarray.Dataset

        """
        if isinstance(index, int):
            path_file = self.output.get_field_file(prefix, index)
            ds = pm.open_dataset(path_file, **kwargs)
        elif isinstance(index, str):
            case = self.output.name_solver
            path = self.output.path_session
            ext = "?????" if index == "all" else index

            pattern = f"{prefix}{case}0.f{ext}"
            ds = pm.open_mfdataset(path / pattern, **kwargs)
        else:
            raise ValueError("Parameter index should be int or str")

        self.data = ds
        return ds

    def get_var(self, key):
        """Return a specific array.

        Parameters
        ----------
        key: str
            Key indicating a DataArray in

        Returns
        -------
        xarray.DataArray
        """
        return self.data[key]


class ReaderPymechStats(ReaderPymech):
    tag = "pymech_stats"

    def open(self, prefix="sts", index=-1, **kwargs):
        """Opens :ref:`statistics` field files(s) as a xarray dataset"""
        return super().open(prefix, index, **kwargs)
