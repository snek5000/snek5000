# snek5000

[![](https://github.com/exabl/snek5000/workflows/Tests/badge.svg)](https://github.com/exabl/snek5000/actions?workflow=Tests)
[![](https://github.com/exabl/snek5000/workflows/Docs/badge.svg)](https://github.com/exabl/snek5000/actions?workflow=Docs)

Python framework for Nek5000.

**Warning:** This framework is experimental and of alpha-quality. The API can also change.

## Installation

```sh 
# Clon e
git clone --recursive git@github.com:exabl/snek5000.git

# Activate paths: Start here. Always!
cd snek5000
source activate.sh

```

## Workflow

### Easy way

This workflow requires you to setup a Python environment. There are two ways to
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

### Why use snek5000?

The [`snek5000` Python
API](https://exabl.github.io/snek5000/_generated/snek5000.html) is based on
[fluidsim](https://fluidsim.readthedocs.io), which allows you to launch a
simulation as follows.

```python
from snek5000.solvers.abl import Simul

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
- Out of source builds and runs
- Avoid typos and human errors
- Better than bash scripting:

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

## Development

See [contributing guidelines](CONTRIBUTING.md).
