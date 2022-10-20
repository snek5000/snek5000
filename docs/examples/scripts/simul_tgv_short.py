from snek5000_tgv.solver import Simul

params = Simul.create_default_params()
params.output.sub_directory = "examples_snek_tgv/short"

params.oper.nx = params.oper.ny = params.oper.nz = 6
params.oper.elem.order = params.oper.elem.order_out = 8

params.nek.general.end_time = 15
params.nek.general.stop_at = "endTime"

"""
TODO: I (pa) don't manage to get adaptative dt. How whould I do that? Where is
the documentation for that?

TODO: I get only:

In [3]: params.nek.general._print_docs()
Documentation for info_simul.params.nek.general
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
"""
params.nek.general.dt = 0.05

params.nek.general.target_cfl = 2.0
params.nek.general.time_stepper = "BDF3"
params.nek.general.extrapolation = "OIFS"

params.nek.general.write_control = "runTime"
params.nek.general.write_interval = 1.0

sim = Simul(params)
sim.make.exec("run_fg")

print(
    f"""
One can load this simulation with

cd {sim.output.path_run}; ipython --matplotlib -i -c "from snek5000 import load; sim = load()"

Then, some figures/movies can be produced with, for example:

sim.output.phys_fields.plot_hexa()
sim.output.phys_fields.animate(dt_frame_in_sec=0.1, vmin=-1, vmax=1, interactive=True)
sim.output.phys_fields.animate(dt_frame_in_sec=0.1, vmin=-1, vmax=1, save_file="~/movie.gif")
"""
)
