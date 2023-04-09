# How to control Fortran warnings during compilation

By default Snek5000 suppresses the compilation warnings. This is because Nek5000 uses a
lot of *legacy tricks* to achieve high performance which triggers warnings in modern C
and Fortran compilers.

To display the warnings one should adjust the `verbosity` keyword argument for
[`Output.update_snakemake_config`](snek5000.output.base.Output.update_snakemake_config).
For example in your solver's Snakemake file

```{code-block} python
---
emphasize-lines: 6
---
from snek5000 import ensure_env, get_snek_resource
from snek5000_canonical import short_name, Output

configfile: "config_simul.yml"

Output.update_snakemake_config(config, short_name, verbosity=1)
```

## How to halt compilation if Fortran warnings arise from case file (`*.usr`)

Fortran warnings from Nek5000 code-base maybe inevitable, but it is indeed
possible to keep the case file tidy and subject to a stricter set of Fortran
convention.
