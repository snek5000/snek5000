# How to run the tests

## As in the CI with `nox`

Our tests are run on Github Actions with

```sh
nox --session tests-cov -- -v --runslow --cov-report=xml
```

So the following command can be useful

```sh
# first time (creation of the environment)
nox -s tests-cov
# after the creation of the environment
nox -s tests-cov -r --no-install
nox -s tests-cov -r --no-install -- -v --runslow
```

With the session `tests` instead of `tests-cov`, no coverage report is created.

## Manually without `nox`

Of course, if can be very useful to launch some tests manually. With the test or dev
dependencies installed, one can run for example:

```sh
pytest tests
pytest --runslow tests/test_restart.py
pytest --runslow tests/test_restart.py::test_restart_new_dir_results
pytest -h | grep pdb
pytest tests/test_files.py --pdb --pdbcls=IPython.terminal.debugger:TerminalPdb
```
