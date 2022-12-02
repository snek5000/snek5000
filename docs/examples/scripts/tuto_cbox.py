import builtins
import os
import signal
from time import perf_counter, sleep

import numpy as np
from scipy.signal import argrelmax
from snek5000_cbox.solver import Simul

from fluiddyn.util import time_as_str

params = Simul.create_default_params()

aspect_ratio = 1.0
params.prandtl = 0.71

# The onset of oscillatory flow for aspect ratio 1.0 is at Ra_c = 1.825e8
params.Ra_side = 2e8

params.output.sub_directory = "examples_snek/tuto"

params.oper.dim = 2
params.oper.nproc_min = 2

nb_elements = ny = 8
params.oper.ny = nb_elements
nx = params.oper.nx = int(nb_elements / aspect_ratio)

Ly = params.oper.Ly
Lx = params.oper.Lx = Ly / aspect_ratio

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
params.nek.pressure.residual_tol = 1e-05

params.nek.general.end_time = 1000
params.nek.general.stop_at = "endTime"
params.nek.general.target_cfl = 2.0
params.nek.general.time_stepper = "BDF3"
params.nek.general.extrapolation = "OIFS"

params.nek.general.write_control = "runTime"
params.nek.general.write_interval = 50

params.output.history_points.write_interval = 10


if __name__ == "__main__":
    sim = Simul(params)

    # to save the PID of the simulation (a number associated with the process)
    sim.output.write_snakemake_config(
        custom_env_vars={"MPIEXEC_FLAGS": "--report-pid PID.txt --oversubscribe"}
    )
    # run the simulation in the background (non blocking call)
    sim.make.exec("run", nproc=2)

    pid_file = sim.path_run / "PID.txt"

    # we wait for the simulation to be started and the PID file to be created
    n = 0
    while not pid_file.exists():
        sleep(1)
        n += 1
        if n > 60:
            raise RuntimeError(f"{pid_file} does not exist.")

    with open(pid_file) as file:
        pid = int(file.read().strip())

    # we know the PID of the simulation so we can control it!

    # a simple way to print in stdout and in a file
    path_log_py = sim.path_run / f"log_py_{time_as_str()}.txt"

    def print(*args, sep=" ", end="\n", **kwargs):
        builtins.print(*args, **kwargs)
        with open(path_log_py, "a") as file:
            file.write(sep.join(str(arg) for arg in args) + end)

    print(f"{pid = }")

    def check_running():
        """Check for the existence of a running process"""
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    while check_running():
        sleep(2)
        t0 = perf_counter()
        coords, df = sim.output.history_points.load_1point(
            index_point=12, key="temperature"
        )
        t_last = df.time.max()
        print(
            f"{time_as_str()}, {t_last = :.2f}: "
            f"history_points loaded in {perf_counter() - t0:.2f} s"
        )

        if t_last < 500:
            continue

        temperature = df.temperature.to_numpy()
        times = df.time.to_numpy()

        temperature = temperature[times > 500]
        times = times[times > 500]

        # we know that there are oscillations growing exponentially
        # we look for the positive maxima of the signal
        indices_maxima = argrelmax(temperature)
        temp_maxima = temperature[indices_maxima]
        temp_maxima = temp_maxima[temp_maxima > 0]

        # similar to a second order derivative
        diff_maxima = np.diff(np.diff(temp_maxima))

        if any(diff_maxima < 0):
            # as soon as the growth starts to saturate
            print(
                f"Saturation of the instability detected at t = {t_last}\n"
                "Terminate simulation."
            )

            os.kill(pid, signal.SIGTERM)
            break
