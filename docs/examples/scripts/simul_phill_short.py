from phill.solver import Simul

params = Simul.create_default_params()

params.output.sub_directory = "examples_phill/short"

params.oper.nx = 12
params.oper.ny = 10
params.oper.nz = 8

params.oper.nproc_min = 2

params.nek.general.num_steps = 100
params.nek.general.time_stepper = "bdf2"
params.nek.general.write_interval = 10

params.nek.stat.av_step = 2
params.nek.stat.io_step = 10

sim = Simul(params)

sim.make.exec("run_fg")

print(
    f"""
One can load this simulation with

cd {sim.output.path_run}; ipython --matplotlib -i -c "from snek5000 import load; sim = load()"

Then, some figures/movies can be produced with, for example:

sim.output.phys_fields.plot_hexa()
sim.output.phys_fields.animate(dt_frame_in_sec=0.1, vmin=-1, vmax=0.3, interactive=True)
sim.output.phys_fields.animate(dt_frame_in_sec=0.1, vmin=-1, vmax=0.3, save_file="~/movie.gif")
"""
)
