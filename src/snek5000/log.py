"""Logging
==========
A logger instance (variable :code:`logger`).

"""

import logging
import os

logger = logging.getLogger(__name__)


def create_handler(width=None):
    try:
        from rich.console import Console
        from rich.logging import RichHandler

        console = Console(width=width, stderr=True)
        handler = RichHandler(console=console, show_time=False, show_path=False)
    except ImportError:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    return handler


handler = create_handler()
logger.addHandler(handler)


if os.getenv("SNEK_DEBUG"):
    level = logging.DEBUG
else:
    level = logging.INFO

logger.setLevel(level)
