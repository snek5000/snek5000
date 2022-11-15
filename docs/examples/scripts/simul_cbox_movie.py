from tuto_cbox import Simul, params

params.output.sub_directory = "examples_snek/movie"

aspect_ratio = 0.8
params.prandtl = 0.71
params.Ra_side = 8e9
nb_elements = 12
order = 10

Ly = params.oper.Ly
params.oper.Lx = Ly / aspect_ratio

params.oper.ny = ny = nb_elements
nx = params.oper.nx = int(nb_elements / aspect_ratio)

params.oper.elem.order = params.oper.elem.order_out = order

params.short_name_type_run = f"Ra{params.Ra_side:.3e}_{nx*order}x{ny*order}"

params.nek.general.write_interval = 1
params.nek.general.end_time = 100
params.nek.general.target_cfl = 1.7

params.nek.velocity.residual_tol = 1e-08
params.nek.pressure.residual_tol = 1e-06

sim = Simul(params)

sim.make.exec("run_fg", nproc=4)

print(f"""You can run:

cd {sim.output.path_run}; snek-ipy-load

Then, from IPython:

from functools import partial

animate = partial(
    sim.output.phys_fields.animate, dt_frame_in_sec=0.02, dt_equations=0.5,
    pcolor_kw=dict(cmap="coolwarm")
)

animate(interactive=True)
animate(save_file="movie.gif")

""")
