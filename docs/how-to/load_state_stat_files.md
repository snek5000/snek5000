# How to load and represent data saved in state and stat files

Nek5000 saves the state of the simulation in binary files with a specific format and
names like `phill0.f00001`. The same format is used by the stat extension of the KTH
framework with slightly different names (`stsphill0.f00001`). Snek5000 provides
different tools to load and represent such data:

## As hexahedral data

Different specialized methods of `sim.output.phys_fields` (see
{class}`snek5000.output.phys_fields.PhysFields`) are available to work with hexahedral
data: `read_hexadata`, `plot_hexa`,
{func}`fluidsim_core.output.movies.MoviesBase.animate`, `read_hexadata_stat`,
`plot_hexa_stat`. An advantage is that it works even for stretched meshes.

Examples are given in
[a specific section of the tutorial using `snek5000-phill`](../tuto_phill_script.myst.md#read-and-plot-state-and-stat-files-as-hexahedral-data).

## As xarray datasets

Examples are given in
[a specific section of the tutorial using `snek5000-cbox`](../tuto_cbox.myst.md#load-the-flow-field-as-xarray-dataset).

For stat data, one needs to change the reader with:

```python
sim.output.phys_fields.change_reader("pymech_stats")
xarr = sim.output.phys_fields.load()
```
