import logging
import os
from pathlib import Path

import pytest

from snek5000.output.base import Output

xdg_config = Path(os.path.expandvars(os.getenv("XDG_CONFIG_HOME", "$HOME/.config")))
configfile_xdg_config = xdg_config / "snek5000.yml"


def test_update_snakemake_config():
    # Dummy config values
    config = {
        key: ""
        for key in (
            "CC",
            "FC",
            "MPICC",
            "MPIFC",
            "MPIEXEC",
            "MPIEXEC_FLAGS",
            "CFLAGS",
            "FFLAGS",
        )
    }
    name_solver = "base"
    Output.update_snakemake_config(config, name_solver)

    expected_keys = {"CASE", "file", "includes", "objects"}
    assert expected_keys.issubset(config)

    original_case = config["CASE"]
    os.environ["CASE"] = "test_config"

    Output.update_snakemake_config(config, name_solver, env_sensitive=True)
    assert original_case != "test_config"
    assert config["CASE"] == "test_config"

    os.environ["SNEK_ENV_SENSITIVE"] = "1"
    os.environ["CASE"] = "test_config_1"
    Output.update_snakemake_config(config, name_solver)
    assert config["CASE"] == "test_config_1"

    os.environ["SNEK_ENV_SENSITIVE"] = "0"
    os.environ["CASE"] = "test_config_2"
    Output.update_snakemake_config(config, name_solver)
    assert config["CASE"] == original_case


@pytest.mark.skipif(
    configfile_xdg_config.exists(), reason=f"File {configfile_xdg_config} exists"
)
def test_get_configfile(caplog):
    hostname = "test_config"

    Output.get_configfile(host=hostname)

    for logger_name, level, message in caplog.record_tuples:
        if (
            logger_name == "snek5000.log"
            and level == logging.WARNING
            and "Missing a configuration file" in message
        ):
            assert f"{hostname}.yml" in message
            break
    else:
        raise IOError("Expected a warning message when configuration file is missing")
