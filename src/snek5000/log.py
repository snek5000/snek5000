"""Logging
==========
A logger instance (variable :code:`logger`).

"""

import logging
import os


def create_handler(width=None):
    try:
        from rich.console import Console
        from rich.logging import RichHandler

        console = Console(width=width, stderr=True)
        return RichHandler(console=console)
    except ImportError:
        return logging.StreamHandler()


handler = create_handler()
logger = logging.getLogger(__name__)

# adding a logging.StreamHandler leads to buggy logging
# see https://github.com/snek5000/snek5000/issues/38
try:
    import rich
except ImportError:
    pass
else:
    logger.addHandler(handler)


if os.getenv("SNEK_DEBUG"):
    level = logging.DEBUG
else:
    level = logging.INFO


logger.setLevel(level)
