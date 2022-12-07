---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

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

Snek5000 is a unified framework providing a Python API and shell commands to
help us for these different steps. These tutorials present how it works in
practice.

```

**Versions used in these tutorials:**

```{code-cell} ipython3
!snek-info
```

```{toctree}
---
maxdepth: 2
---
tuto_phill_setup.myst.md
tuto_phill_make.myst.md
tuto_phill_script.myst.md
tuto_tgv.myst.md
tuto_cbox.myst.md
tuto_config.rst
tuto_packaging.rst
```

The snek5000-cbox repository contains
[scripts used for a real life study](https://github.com/snek5000/snek5000-cbox/tree/main/doc/examples)
that can be interesting for any Snek5000 users.
