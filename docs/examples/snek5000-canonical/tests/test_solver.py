import pytest


def test_init(sim):
    print(sim.info_solver)
    pass


def test_mesh(sim):
    assert sim.make.exec("mesh")


def test_compile(sim):
    assert sim.make.exec("compile")
    assert sim.make.exec("run", dryrun=True)
