import sys
from unittest.mock import patch

import pytest
from conftest import unset_snek_debug
from pymech.neksuite.field import read_header

from snek5000 import load
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


def _test_run(sim_executed, capsys, command, end_time):
    with patch.object(sys, "argv", command):
        with unset_snek_debug():
            main()

    out = capsys.readouterr().out
    path_new = out.split("# To visualize with IPython:\n\ncd ")[-1].split(";")[0]
    sim = load(path_new)
    assert sim_executed.path_run != sim.path_run
    assert (sim.path_run / "session_00").exists()

    header = read_header(sim.output.get_field_file())
    assert header.time == end_time


@pytest.mark.slow
def test_restart_command_run(sim_cbox_executed_readonly, capsys):
    end_time = 0.012
    command = [
        "snek-restart",
        str(sim_cbox_executed_readonly.output.path_run),
        "--use-checkpoint",
        "1",
        "--new-dir-results",
        "--end-time",
        str(end_time),
    ]
    _test_run(sim_cbox_executed_readonly, capsys, command, end_time)


@pytest.mark.slow
def test_restart_command_run_start_from(sim_cbox_executed, capsys):
    end_time = 0.012
    command = [
        "snek-restart",
        sim_cbox_executed.output.path_run,
        "--use-start-from",
        "-1",
        "--new-dir-results",
        "--end-time",
        str(end_time),
    ]
    _test_run(sim_cbox_executed, capsys, command, end_time)
