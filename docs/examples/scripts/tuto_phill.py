from phill.solver import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_snek/tuto"
params.oper.nx = 6
params.oper.ny = 5
params.oper.nz = 4
params.oper.elem.order = params.oper.elem.order_out = 8

params.oper.nproc_min = 2

params.nek.general.num_steps = 10
params.nek.general.time_stepper = "bdf2"
params.nek.general.write_interval = 10

params.nek.stat.av_step = 2
params.nek.stat.io_step = 10

sim = Simul(params)

sim.make.exec("run_fg", nproc=2)
