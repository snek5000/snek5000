"""Utility for configuration files"""

import os
import shutil
from pathlib import Path
from socket import gethostname

from snek5000 import get_snek_resource


def ensure_config_file():
    """Ensure that a configuration file is present.

    This function is used by the console script `snek-generate-config`.
    """
    host = os.getenv("SNIC_RESOURCE", os.getenv("GITHUB_WORKFLOW", gethostname()))
    xdg_config = Path(os.path.expandvars(os.getenv("XDG_CONFIG_HOME", "$HOME/.config")))
    configfile_xdg_config_host = xdg_config / f"snek5000/{host}.yml"
    configfile_xdg_config = xdg_config / "snek5000.yml"

    config_files = [configfile_xdg_config_host, configfile_xdg_config]
    config_files = [path for path in config_files if path.exists()]

    if not config_files:
        print("No user config file found")
        configfile_default = Path(get_snek_resource("default_configfile.yml"))
        print(f"Copying {configfile_default} to {configfile_xdg_config}")
        configfile_xdg_config.parent.mkdir(exist_ok=True)
        shutil.copyfile(configfile_default, configfile_xdg_config)
    else:
        print(f"Found configuration file {config_files[0]}")
