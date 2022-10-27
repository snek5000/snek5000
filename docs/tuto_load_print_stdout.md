---
jupytext:
  text_representation:
    format_name: myst
kernelspec:
  display_name: Python 3
  name: python3
execution:
  timeout: 300
---

<!-- #region tags=[] -->
# Loading simulations and visualizing data from standard output

## Verification of Taylor-Green vortex case

See [`snek5000-tgv`](https://github.com/snek5000/snek5000/tree/main/docs/examples/snek5000-tgv) for the implementation. The simulation was executed as follows:

```{code-cell}
from snek5000_tgv.solver import Simul


params = Simul.create_default_params()
sim = Simul(params)
sim.make.exec("run_fg")
```

Here we load and process the output.
<!-- #endregion -->

```{code-cell}
from snek5000 import load

sim = load(sim.path_run)
```

## Visualize raw data via ``sim.output.print_stdout``

In subroutine `userchk` of `tgv.usr.f`, the time stamp, kinetic energy and enstrophy are output into standard output, with a keyword `monitor` at the end of the line. We can use regular expressions to extract these lines. If you are new to regular expressions, this website can help you <https://regex101.com/>.

```{code-cell}
import re

monitor = re.findall('(.*)monitor$', sim.output.print_stdout.text, re.MULTILINE)
monitor
```

It is also possible to achieve the same using Python's string manipulation and list comprehension:

```{code-cell}
monitor = [
    line[:-len("monitor")]  # Or in Python >= 3.9, line.removesuffix("monitor")
    for line in sim.output.print_stdout.text.splitlines()
    if line.endswith("monitor")
]
```

```{code-cell}
import pandas as pd

df = pd.DataFrame(
    ((float(value) for value in line.split()) for line in monitor),
    columns=("time", "energy", "enstrophy")
)
df.head()
```

### Reference data

```{code-cell}
ref = pd.read_csv(
    "examples/snek5000-tgv/ref_data_spectral_code.csv",
    sep=" ",
    names=("time", "ref:energy", "ref:dE/dt", "ref:enstrophy"),
    comment="#"
)
ref.head()
```

### Result

```{code-cell} tags=[]
ax = df.plot("time", ["enstrophy", "energy"], logy=True, colormap="Accent")
ref.plot(
    "time",
    ["ref:enstrophy", "ref:energy"],
    ax=ax,
    style="--",
    logy=True,
    colormap="Accent"
)
_ = ax.set(
    title=f"Taylor-Green vortex: evolution of K.E. and enstrophy. Re={-sim.params.nek.velocity.viscosity}"
)
```
