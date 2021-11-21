import re
from pathlib import Path

from snek5000.log import logger

pattern = r"""
(?P<file>[^:^\n]+):(?P<line_nb>\d+):(?P<col>\d+):\n{,3}              # Filename and location: file, line_nb, col
(\s*?(?P<L>\d+?)\ \|(?P<source>.*?)$\n\s*?\|(?P<mark>.*?\d)\n\.*?)*  # Source code: L, source, mark
^(?P<level>Warning|Error):\ (?P<msg>.*)                              # Reason: level, msg
"""

expr = re.compile(pattern, re.MULTILINE | re.VERBOSE)


def log_match(match, levels):
    """Display a match which is included in the levels requested.

    Parameters
    ----------
    match : re.Match
        A regular expression match
    levels : iterable of str
        Should by a subset of `{"Error", "Warning"}`

    """
    if match["level"] in levels:
        logger.info(
            f"{match['level']}: "
            f"{match['file']}:{match['line_nb']}:{match['col']}\n"
            f"{match.group(match.lastindex)}\n"
            #  match["source"],
        )


def log_matches(path_log, levels=("Error", "Warning")):
    """Log all matches

    Parameters
    ----------
    path_log : str or path-like
        Path to a log file with gfortran compilation output
    levels : iterable of str
        Should by a subset of `{"Error", "Warning"}`
    """
    text = Path(path_log).read_text()
    for match in expr.finditer(text):
        log_match(match, levels=["Error"])
