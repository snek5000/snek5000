# eturb
Efficient simulations of turbulent atmospheric boundary layer.

## Getting started

```sh
# Clone
git clone --recursive git@github.com:exabl/eturb.git

# Activate paths: Start here. Always!
cd eturb
source activate.sh

# Build Nek5000
cd lib/Nek5000/tools/
./maketools all
cd -

# Build case
cd src/abl_nek5000/
makenek
cd -

# Run case
cd src/abl_nek5000/
nekmpi <nb_procs> # foreground
nekbmpi <nb_procs> # background
cd -

```

## Development

See [contributing guidelines](CONTRIBUTING.md).
