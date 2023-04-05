# How to load and plot history points

## Parameters for simulation with history points

To generate history points, one needs to specify in a Snek5000 solver,

```py
params.output.history_points.write_interval: int = ...
params.output.history_points.coords: list[tuple[float, float, float] | tuple[float, float]] = ...
```

For example, see the
[parameters used in the tutorial for snek5000-cbox](../tuto_cbox.myst.md#a-more-advanced-script-adapted-for-a-particular-instability).

This should be coupled along with a `hpts()` call in `userchk()` subroutine in the
Nek5000 user file. For more information, see *documentation for
`params.output.history_points`* in {class}`snek5000.output.base.Output`.

## Loading and plotting

Use `load*` and `plot*` methods in class
{class}`snek5000.output.history_points.HistoryPoints`. A working example of this can be
found in
[a tutorial where we process results from a snek5000-cbox simulation](../tuto_cbox.myst.md#load-and-plot-history-points-data).
