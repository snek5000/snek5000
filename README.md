<div align="center">

# Snek5000

[![PyPI](https://img.shields.io/pypi/v/snek5000)](https://pypi.org/project/snek5000/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/snek5000/snek5000/build.yaml?branch=main)](https://github.com/snek5000/snek5000/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/snek5000/snek5000/main.svg)](https://results.pre-commit.ci/latest/github/snek5000/snek5000/main)
[![Documentation Status](https://readthedocs.org/projects/snek5000/badge/?version=latest)](https://snek5000.readthedocs.io/en/latest/?badge=latest)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=snek5000_snek5000&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=snek5000_snek5000)
[![Code coverage](https://codecov.io/gh/snek5000/snek5000/branch/main/graph/badge.svg?token=WzGnN0dfbw)](https://codecov.io/gh/snek5000/snek5000)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7399621.svg)](https://doi.org/10.5281/zenodo.7399621)

<!-- badges -->

Python framework for Nek5000

</div>

**Documentation**: <https://snek5000.readthedocs.io/>

Snek5000 is a Python package which allows one to write [Fluidsim] solvers based
for the simulations on the Fortran [CFD] code [Nek5000]. There are open-source
solvers (in particular [snek5000-phill], [snek5000-cbox] and [snek5000-tgv])
and it's not difficult to write your own solver based on your Nek5000 cases (as
shown in [this
tutorial](https://snek5000.readthedocs.io/en/latest/tuto_packaging.html)).

With a Snek5000-Fluidsim solver, it becomes very easy to

- launch/restart simulations with Python scripts and terminal commands,
- load simulations, read the associated parameters/data and produce nice
  figures/movies.

Snek5000 can be seen as a workflow manager for Nek5000 or a Python wrapper
around Nek5000. It uses Nek5000 on the background and is thus NOT a rewrite of
Nek5000!

Snek5000 is powered by nice Python packages such as [Snakemake], [Fluidsim],
[Pymech], Matplotlib, Jinja, Pytest, Xarray, etc.

## Quick start

Install it as follows:

```sh
export NEK_SOURCE_ROOT="/path/to/Nek5000"

pip install snek5000
```

See here for
[detailed installation instructions and notes on incompatible Nek5000 versions](https://snek5000.readthedocs.io/en/latest/install.html).

### Why Snek5000?

The [`snek5000` Python
API](https://snek5000.readthedocs.io/en/latest/_generated/snek5000.html) allows
you to launch/restart/load simulations. For example, the [periodic hill Nek5000
example](https://nek5000.github.io/NekDoc/tutorials/perhill.html) can be
launched with our [snek5000-phill] solver (installable with `pip install snek5000-phill`) as follows:

```python
from phill.solver import Simul

params = Simul.create_default_params()

# modify parameters as needed, for example
params.output.sub_directory = "examples_snek_phill"
params.short_name_type_run = "readme"

params.oper.nx = 12
params.oper.ny = 10
params.oper.nz = 8

params.nek.general.write_interval = 4
params.nek.general.num_steps = 12

...

# instantiate the object representing the simulation
sim = Simul(params)

# compile and launch the simulation (blocking)
sim.make.exec("run_fg")
```

A simulation directory is created automatically (with this example, something
like
`~/Sim_data/examples_snek_phill/phill_readme_12x10x8_V1.x1.x1._2022-10-27_15-21-58`).
Then, the simulation object can be recreated from this directory. An easy way
would be to go into this directory, start IPython with the `snek-ipy-load`
command. Then, to post-process the results run:

```python
# get/print the simulation parameters from the object
sim.params

# few examples of various read and plots
sim.output.print_stdout.plot_dt_cfl()
sim.output.print_stdout.plot_nb_iterations()

sim.output.phys_fields.plot_hexa()
sim.output.phys_fields.animate("pressure", interactive=True)
sim.output.phys_fields.animate(
    "pressure", dt_frame_in_sec=0.1, equation="y=0.5", save_file="my_great_movie.gif"
)
```

As another example, this movie has been produced by a `sim.output.phys_fields.animate`
call from a [snek5000-cbox]
[simulation](https://github.com/snek5000/snek5000/blob/main/docs/examples/scripts/simul_cbox_movie.py):

https://user-images.githubusercontent.com/8842662/202872147-4ea3c749-dc63-4a73-98a0-6c787edb9cd3.mp4

Solvers can also have extra capabilities such as
[processing data from history points](https://snek5000.readthedocs.io/en/latest/how-to/history_points.html).
To see how this works, run a short [snek5000-cbox] simulation
[script where history points are defined](https://github.com/snek5000/snek5000-cbox/blob/main/doc/examples/run_side_short.py),
change to the simulation directory, execute `snek-ipy-load` command and then

```python
# Plot all history points
sim.output.history_points.plot()
# Print the coordinates of the history points
sim.output.history_points.coords
# Load one history point as a dataframe for further post-processing
coords, data = sim.output.history_points.load_1point(2)
```

![](https://raw.githubusercontent.com/snek5000/snek5000/main/docs/_static/history_points.png)

Check out the
[tutorials](https://snek5000.readthedocs.io/en/latest/tutorials.html) to learn
how to use Snek5000.

<details>
<summary>
<b>
Need more reasons to use snek5000?
</b>
</summary>

#### Advantages

##### Parameters, get started without studying the whole documentation

- Saves you from the trouble in setting up multiple source files (`.box`, `.par`, `SIZE`)
- Uses sensible names and defaults for the parameters
- Avoids typos and human errors thanks to a nice [parameter container object]
- Records metadata related to the simulation into human and machine readable files (`params_simul.xml`, `config_simul.yml`)
- Checks for consistency of parameters
- Automatically sets some parameters as Python properties

##### Workflow

- Out of source build (per run), which can be inspected or executed using the
  conventional `makenek` for debugging

- Reproducible workflows, not susceptible to changes in environment variables by default

- Scriptable simulation execution allowing parametric studies

- Easy to load simulation for performing offline post-processing and restarting the simulation

- Better than Bash scripting like:

  ```sh
  # Build case
  cd src/phill/
  CASE="phill"
  echo "$CASE.box" | genbox
  mv -f box.re2 phill.re2
  echo "$CASE\n0.01" | genmap
  FFLAGS="-mcmodel=medium -march=native" CFLAGS="-mcmodel=medium -march=native" makenek
  cd -

  # Run case
  cd src/phill/
  nekmpi $CASE <nb_procs> # foreground
  nekbmpi $CASE <nb_procs> # background
  cd -

  # Clean
  makenek clean
  ```

- Use of [Snakemake](https://snakemake.readthedocs.io/en/stable/) which is
  similar to GNU Make, but allows one to blend Bash and Python scripting and uses
  simple YAML files for managing custom configurations of compilers and flags for
  different computers.

##### Coding

- User friendly, modular, object oriented API
- Reuse of code (inheritance)
- Tested with a good code coverage (>90%)

#### Disadvantages

- Yet another layer... with the possible associated bugs :-)
- Requires some basic knowledge of Python to use (*not really a big issue, to
  be honest*).
- Deep modification of solvers requires learning how
  [Snakemake](https://snakemake.readthedocs.io/en/stable/) functions and [how
  to write Jinja
  templates](https://jinja.palletsprojects.com/en/2.11.x/templates/) (which are
  [not so hard](https://snek5000.readthedocs.io/en/latest/how-to/templates.html), btw)

</details>

## Contributing

Contributions are welcome! You can help by testing out the code, filing issues
and submitting patches. See [contributing guidelines](CONTRIBUTING.md).

[cfd]: https://en.wikipedia.org/wiki/Computational_fluid_dynamics
[fluidsim]: https://fluidsim.readthedocs.io
[nek5000]: https://nek5000.mcs.anl.gov/
[parameter container object]: https://fluiddyn.readthedocs.io/en/latest/generated/fluiddyn.util.paramcontainer.html
[pymech]: https://github.com/eX-Mech/pymech
[snakemake]: https://snakemake.readthedocs.io
[snek5000-cbox]: https://github.com/snek5000/snek5000-cbox
[snek5000-phill]: https://github.com/snek5000/snek5000-phill
[snek5000-tgv]: https://github.com/snek5000/snek5000/tree/main/docs/examples/snek5000-tgv
