"""Cluster utilities"""
import os

from .log import logger


def _int_getenv(key, default=0):
    return int(os.getenv(key, default))


def _slurm():
    """Check different environment variables available within a SLURM job.

    .. seealso::

        https://slurm.schedmd.com/srun.html#SECTION_OUTPUT-ENVIRONMENT-VARIABLES

    """
    return _int_getenv("SLURM_NPROCS") or (
        _int_getenv("SLURM_NNODES") * _int_getenv("SLURM_CPUS_ON_NODE")
    )


def _oar():
    """Equivalent to  the shell command::

    NPROC=$(cat ${OAR_NODEFILE} | wc -l).

    """
    nodefile = os.getenv("OAR_NODEFILE")
    if nodefile and os.path.exists(nodefile):
        with open(nodefile) as file:
            return len(file.readlines())
    else:
        return 0


def nproc_available():
    """Detect maximum number of processors available

    Returns
    -------
    int

    """
    # Inside job schedulers, number of processors assigned will vary
    # TODO: extend this function for other schedulers PBS etc.
    cluster_nproc = _slurm() or _oar()

    if cluster_nproc:
        var = "Cluster environment variables"
        nproc = cluster_nproc
    else:
        var = "os.cpu_count()"
        nproc = os.cpu_count()

    logger.debug(f"Using {var} to detect maximum number of processors available")
    return nproc
