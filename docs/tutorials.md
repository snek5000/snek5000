# Tutorials

```{admonition} Preliminary: introduction on Nek5000 classical workflow

Let's recall that working with Nek5000 involves:

- setting up a directory with different files defining a simulation, in
particular (for a case called `phill`), `phill.usr` defining Fortran functions,
`phill.par`, `phill.box` and `SIZE` containing parameters, `SESSION.NAME`, etc.

- running commands to create the mesh, compile and launch the simulation.

To restart a simulation or create another simulation from a previous one, other
manual file manipulations are necessary.

Then, some output files can be analyzed and used to produce figures and movies.

Snek5000 is a unified framework providing a Python API and commands to help us
for these different steps. These tutorials present how it work in practice.

```

```{toctree}
---
maxdepth: 2
---
tuto_phill_setup.md
configuring
tuto_phill.md
tuto_tgv.md
tuto_cbox.md
packaging.rst
```

The snek5000-cbox repository contains
[real life scripts](https://github.com/snek5000/snek5000-cbox/tree/main/doc/examples)
that can be interesting for any Snek5000 users.
