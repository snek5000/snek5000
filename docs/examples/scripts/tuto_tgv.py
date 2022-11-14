from snek5000_tgv.solver import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_snek/tuto"

params.oper.nx = params.oper.ny = params.oper.nz = 8
params.oper.elem.order = params.oper.elem.order_out = 8
params.oper.nproc_min = 2

params.nek.velocity.residual_tol = 1e-07
params.nek.pressure.residual_tol = 1e-05

params.nek.general.end_time = 15
params.nek.general.dt = -1
params.nek.general.target_cfl = 1.4
params.nek.general.extrapolation = "OIFS"

sim = Simul(params)
sim.make.exec("run_fg", nproc=2)
