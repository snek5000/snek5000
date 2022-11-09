import numpy as np

from snek5000_cbox.solver import Simul

params = Simul.create_default_params()

aspect_ratio = 1.0
params.prandtl = 0.71

params.Ra_side = 2.0e8

params.output.sub_directory = "examples_snek/tuto"

params.oper.dim = 2
params.oper.nproc_min = 2

nb_elements = ny = 20
params.oper.ny = nb_elements
nx = params.oper.nx = int(nb_elements / aspect_ratio)
params.oper.nz = int(nb_elements / aspect_ratio)

Ly = params.oper.Ly
Lx = params.oper.Lx = Ly / aspect_ratio
Lz = params.oper.Lz = Ly / aspect_ratio

order = params.oper.elem.order = params.oper.elem.order_out = 8

params.oper.mesh_stretch_factor = 0.1  # zero means regular

params.short_name_type_run = f"Ra{params.Ra_side:.3e}_{nx*order}x{ny*order}"

# creation of the coordinates of the points saved by history points
n1d = 5
small = Lx / 10

xs = np.linspace(0, Lx, n1d)
xs[0] = small
xs[-1] = Lx - small

ys = np.linspace(0, Ly, n1d)
ys[0] = small
ys[-1] = Ly - small

coords = [(x, y) for x in xs for y in ys]

params.output.history_points.coords = coords
params.oper.max.hist = len(coords) + 1

params.nek.velocity.residual_tol = 1e-08
params.nek.pressure.residual_tol = 1e-06

params.nek.general.end_time = 500
params.nek.general.stop_at = "endTime"
params.nek.general.target_cfl = 2.0
params.nek.general.time_stepper = "BDF3"
params.nek.general.extrapolation = "OIFS"

params.nek.general.write_control = "runTime"
params.nek.general.write_interval = 10

params.output.history_points.write_interval = 30

sim = Simul(params)
sim.make.exec('run_fg', resources={"nproc": 2})
