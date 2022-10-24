"""Snakemake helper utilities"""
import os


def ensure_env():
    """Ensure environment variables ``NEK_SOURCE_ROOT`` and ``PATH`` are
    intact.

    """
    from .. import get_nek_source_root

    NEK_SOURCE_ROOT = get_nek_source_root()

    if not os.getenv("NEK_SOURCE_ROOT"):
        os.environ["NEK_SOURCE_ROOT"] = NEK_SOURCE_ROOT

    if NEK_SOURCE_ROOT not in os.getenv("PATH"):
        os.environ["PATH"] = ":".join([NEK_SOURCE_ROOT + "/bin", os.getenv("PATH")])


def set_compiler_verbosity(config, verbosity):
    """Set Fortran compiler warnings verbosity:

    Parameters
    ----------
    config: dict
    verbosity: int
        - 0 == suppress warnings
        - 1 == do nothing
        - 2 == all warnings

    """
    flags = {0: " -w ", 1: "", 2: " -Wall "}
    warning_flag = flags[int(verbosity)]
    config["FFLAGS"] = config.get("FFLAGS", "") + warning_flag
    config["CFLAGS"] = config.get("CFLAGS", "") + warning_flag


def append_debug_flags(config):
    """Append to commonly used gcc / gfortran debug flags if ``SNEK_DEBUG``
    environment is activated.

    Parameters
    ----------
    config: dict
        Snakemake configuration. Should contain ``CFLAGS`` and ``FFLAGS`` keys.

    """
    if os.getenv("SNEK_DEBUG"):
        config["CFLAGS"] = config.get("CFLAGS", "") + " -O0 -g"
        config["FFLAGS"] = (
            config.get("FFLAGS", "")
            + " -O0 -g -ffpe-trap=invalid,zero,overflow -DDEBUG "
        )
