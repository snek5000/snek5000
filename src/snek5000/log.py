"""Logging
==========
A logger instance (variable :code:`logger`).

"""

import logging
import os

try:
    from rich.logging import RichHandler

    handler = RichHandler()
except ImportError:
    handler = logging.StreamHandler()

logger = logging.getLogger(__name__)
logger.addHandler(handler)


if os.getenv("SNEK_DEBUG"):
    level = logging.DEBUG
else:
    level = logging.INFO


logger.setLevel(level)
