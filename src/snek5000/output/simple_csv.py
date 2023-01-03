"""Simple specific output with a csv file and a user parameter."""

from abc import ABCMeta
from pathlib import Path

import pandas as pd


class OutputWithCsvFileAndParam(metaclass=ABCMeta):
    INDEX_USERPARAM: int
    _tag: str
    _param_name: str
    _param_default_value: object

    def __init__(self, output=None) -> None:
        self.output = output
        self.path_file = Path(output.path_run) / (self._tag + ".csv")

    @classmethod
    def _complete_params_with_default(cls, params):
        params.output._set_child(
            cls._tag,
            attribs={cls._param_name: cls._param_default_value},
        )
        params.output[cls._tag]._record_nek_user_params(
            {cls._param_name: cls.INDEX_USERPARAM}
        )

    def load(self):
        return pd.read_csv(self.path_file)
