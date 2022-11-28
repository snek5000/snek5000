import sys
from unittest.mock import patch

import pytest

from snek5000.util.restart import main


def test_restart_command_help():
    with patch.object(sys, "argv", ["snek-restart", "-h"]):
        with pytest.raises(SystemExit):
            main()


@pytest.mark.slow
def test_restart_command_only_check(sim_cbox_executed):
    command = [
        "snek-restart",
        sim_cbox_executed.output.path_run,
        "-oc",
        "--new-dir-results",
        "--num-steps",
        "2",
    ]
    with patch.object(sys, "argv", command):
        main()


@pytest.mark.slow
def test_restart_command_only_init(sim_cbox_executed):
    command = [
        "snek-restart",
        sim_cbox_executed.output.path_run,
        "-oi",
        "--new-dir-results",
        "--end-time",
        "0.015",
    ]
    with patch.object(sys, "argv", command):
        main()


@pytest.mark.slow
def test_restart_command_run(sim_cbox_executed):
    command = [
        "snek-restart",
        sim_cbox_executed.output.path_run,
        "--new-dir-results",
        "--add-to-end-time",
        "0.002",
    ]
    with patch.object(sys, "argv", command):
        main()
