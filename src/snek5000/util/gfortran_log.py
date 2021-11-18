import re
import sys

pattern = r"""
(?P<file>[^:^\n]+):(?P<line_nb>\d+):(?P<col>\d+):\n{,3}              # Filename and location: file, line_nb, col
(\s*?(?P<L>\d+?)\ \|(?P<source>.*?)$\n\s*?\|(?P<mark>.*?\d)\n\.*?)*  # Source code: L, source, mark
^(?P<level>Warning|Error):\ (?P<msg>.*)                              # Reason: level, msg
"""

expr = re.compile(pattern, re.MULTILINE | re.VERBOSE)


def print_match(match: re.Match, levels=("Error", "Warning")):
    if match["level"] in levels:
        print(match["level"], end=": ", file=sys.stderr)
        print(
            f"{match['file']}:{match['line_nb']}:{match['col']}\n  ",
            match.group(match.lastindex),
            "\n",
            match["source"],
            file=sys.stderr,
        )
