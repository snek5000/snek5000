# snek5000

[![](https://github.com/exabl/snek5000/workflows/Tests/badge.svg)](https://github.com/exabl/snek5000/actions?workflow=Tests)
[![](https://github.com/exabl/snek5000/workflows/Docs/badge.svg)](https://github.com/exabl/snek5000/actions?workflow=Docs)

Python framework for Nek5000.

**Warning:** This framework is experimental and of alpha-quality. The API can also change.

**Documentation**: https://exabl.github.io/snek5000/

## Installation

```sh 
# Clone
git clone --recursive https://github.com:exabl/snek5000.git

# Activate paths: Start here. Always!
cd snek5000
source activate.sh

```

Now you should setup a Python environment. There are two ways to
do this (and it has to be done only once):

-  Using `venv`
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```
-  Using `conda`
   ```sh
   conda env create -n snek5000 -f environment.yml
   conda activate snek5000
   pip install -e .
   ```

## Why and why not use snek5000?

The [`snek5000` Python
API](https://exabl.github.io/snek5000/_generated/snek5000.html) is based on
[fluidsim](https://fluidsim.readthedocs.io), which allows you to launch a
simulation using scripts. For example the [periodic hill
example](https://github.com/exabl/snek5000-phill) can be launched as.

```python
from phill.solver import Simul

params = Simul.create_default_params()

# modify parameters as needed

sim = Simul(params)
sim.make.exec()  # by default starts a run
sim.make.exec(["mesh", "compile"])  # run rules in order
sim.make.exec(["run"], dryrun=True)  # simulate simulation
sim.make.exec(["run"])  # actual simulation
```

#### Advantages

- Saves you from the trouble in setting up multiple source files (`.box`, `.par`, `SIZE`)
- Checks for consistency of parameters
- Out of source builds and runs, which can be inspected or executed using the conventional
  `makenek` for debugging
- Avoid typos and human errors
- Better than bash scripting like:
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
- Use of [Snakemake](https://snakemake.readthedocs.io/en/stable/) which
  is similar to GNU Make, but allows one to blend bash and python scripting and
  uses simple YAML files for managing custom configurations of compilers and flags
  for different computers.

#### Disadvantages

- In development
- Requires some basic knowledge of Python to use
- Modification of the API requires learning how
  [Snakemake](https://snakemake.readthedocs.io/en/stable/) functions and [how
  to write Jinja
  templates](https://jinja.palletsprojects.com/en/2.11.x/templates/) (which are
  not so hard, btw)

## Roadmap

### Short term
- Implement post processing API: with matplotlib and Paraview

### Long term
- Interface Nek5000 states and time-integration event loop

## Contributing

Contributions are welcome! You can help by testing out the code, filing issues
and submitting patches. See [contributing guidelines](CONTRIBUTING.md).
