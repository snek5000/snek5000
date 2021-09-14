import logging
import os

from snek5000.output.base import Output


def test_update_snakemake_config():
    config = {}
    name_solver = "base"
    Output.update_snakemake_config(config, name_solver)

    expected_keys = {"CASE", "file", "includes", "objects"}
    assert expected_keys.issubset(config)

    original_case = config["CASE"]
    os.environ["CASE"] = "test_config"

    Output.update_snakemake_config(config, name_solver, env_sensitive=True)
    assert original_case != "test_config"
    assert config["CASE"] == "test_config"


def test_get_configfile(monkeypatch, caplog):
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
        raise IOError(
            "Expected a warning message " "when configuration file is missing"
        )
