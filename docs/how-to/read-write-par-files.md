# How to read / write default parameter values from a `*.par` file

Snek5000 is capable of parsing existing `*.par` files. This is shown in the
[`snek5000-tgv` example](../examples/snek5000-tgv/src/snek5000_tgv/solver.py),

```{code-block} python
---
emphasize-lines: 12-14
---
from snek5000.solvers.base import SimulNek
from snek5000.params import complete_params_from_par_file


class SimulTGV(SimulNek):
    ...
    @classmethod
    def create_default_params(cls):
        ...

        # Read defaults for `params.nek` from `tgv.par.cfg` (original code)
        complete_params_from_par_file(
            params, Path(__file__).parent / f"{cls.info_solver.short_name}.par.cfg"
        )
```

This is useful while porting an existing Nek5000 code as a Snek5000 solver.
[See the function's documentation](snek5000.params.complete_params_from_par_file) for
more details.

```{note}
In Snek5000 we follow a convention of renaming the `*.par` file as `*.par.cfg`
in the common source code file to distinguish from the generated `*.par` file
for a specific simulation.
```
