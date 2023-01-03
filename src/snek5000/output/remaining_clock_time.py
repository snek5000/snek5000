"""Plot remaining clock time

"""

from .simple_csv import OutputWithCsvFileAndParam


class RemainingClockTime(OutputWithCsvFileAndParam):
    INDEX_USERPARAM = 12
    _tag = "remaining_clock_time"
    _param_name = "period_save_in_seconds"
    _param_default_value = 5.0
