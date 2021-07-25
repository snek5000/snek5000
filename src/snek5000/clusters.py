"""Cluster utilities"""
import os

from .log import logger


def nproc_available():
    """Detect maximum number of processors available"""

    # Inside job schedulers, number of processors assigened will vary
    # TODO: extend this loop for other schedulers OAR, PBS etc.
    for var in ("SLURM_NPROCS",):
        try:
            nproc = os.environ[var]
        except KeyError:
            continue
        else:
            break
    else:
        var = "os.cpu_count()"
        nproc = os.cpu_count()

    logger.info(f"Using {var} to detect maximum number of processors available")
    return nproc
