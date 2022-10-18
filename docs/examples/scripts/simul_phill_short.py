#!/usr/bin/env python

from phill.solver import Simul

params = Simul.create_default_params()
params.oper.nx = 12
params.oper.ny = 10
params.oper.nz = 8

params.oper.nproc_min = 2

params.nek.general.num_steps = 100
params.nek.general.time_stepper = "bdf2"
params.nek.general.write_interval = 10

params.nek.stat.av_step = 3
params.nek.stat.io_step = 10

sim = Simul(params)

sim.make.exec("run_fg")
