import sys
from unittest.mock import patch

import pytest

from snek5000.util.restart import main


def test_restart_command_help():
    with patch.object(sys, "argv", ["snek-restart", "-h"]):
        with pytest.raises(SystemExit):
            main()


@pytest.mark.slow
def test_restart_command_not_enough_args(sim_cbox_executed):
    command = ["snek-restart", sim_cbox_executed.output.path_run, "-oc"]
    with patch.object(sys, "argv", command):
        with pytest.raises(SystemExit):
            main()


@pytest.mark.slow
def test_restart_command_only_check(sim_cbox_executed):
    command = [
        "snek-restart",
        sim_cbox_executed.output.path_run,
        "-oc",
        "--use-checkpoint",
        "1",
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
        "--use-start-from",
        "-1",
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
        "--use-checkpoint",
        "1",
        "--new-dir-results",
        "--add-to-end-time",
        "0.002",
    ]
    with patch.object(sys, "argv", command):
        main()
