# How to build the documentation

## Old school

With a development environment and from the `docs` directory:

```sh
make cleanall
make
```

## With `nox`

With `nox` installed and from the root directory of the repository:

```sh
# first time (this creates the environment)
nox -s docs
# when the environment has been created
nox -s docs -r --no-install
```
