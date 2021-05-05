"""Snakemake helper utilities"""
import os


def ensure_env():
    """Ensure environment variables ``NEK_SOURCE_ROOT`` and ``PATH`` are
    intact.

    """
    from .. import source_root

    NEK_SOURCE_ROOT = source_root()

    if not os.getenv("NEK_SOURCE_ROOT"):
        os.environ["NEK_SOURCE_ROOT"] = NEK_SOURCE_ROOT

    if NEK_SOURCE_ROOT not in os.getenv("PATH"):
        os.environ["PATH"] = ":".join([NEK_SOURCE_ROOT + "/bin", os.getenv("PATH")])


def append_debug_flags(config, warnings):
    """Append to commonly used gcc / gfortran debug flags if ``SNEK_DEBUG``
    environment is activated.

    Parameters
    ----------
    config: dict
        Snakemake configuration. Should contain ``CFLAGS`` and ``FFLAGS`` keys.
    warnings: bool
        Show most compiler warnings or suppress them.

    """
    warnings_option = "-Wall" if warnings else "-w"
    if os.getenv("SNEK_DEBUG"):
        config["CFLAGS"] += " -O0 -g"
        config["FFLAGS"] += (
            " -O0 -g -ffpe-trap=invalid,zero,overflow -DDEBUG " + warnings_option
        )
