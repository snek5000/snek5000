# How to run a simulation in the foreground / background

By default, executing a simulation as

```{code-block} python
---
emphasize-lines: 5
---
from snek5000_canonical.solver import Simul

params = Simul.create_default_params()
sim = Simul(params)
sim.make.exec('run')
```

would launch the Snakemake rule `run` (default, if not specified) which launches a
simulation in the **background** and returns control to the user. This is useful in
monitoring the simulation. For example see the
[tutorial for snek5000-cbox](../tuto_cbox).

However in HPC clusters you should launch your simulations in the **foreground**, thus
preventing the job from exiting while the simulation is going on. You can also specify
number of MPI processes using the `nproc` keyword argument. For example:

```{code-block} python
---
emphasize-lines: 5
---
nb_nodes = 2
nb_procs_per_node = 32

sim.make.exec(
    'run_fg',
    nproc=nb_nodes * nb_procs_per_node
)
```
