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

# How to export a standalone source code archive which excludes Snek5000

Add the following Snakemake rule to your solver's Snakefile (for example see
[snek5000-phill]):

```python
from phill import short_name, Output

# generate compile.sh
# ===================
rule generate_compile_sh:
    output:
        "compile.sh",
    run:
        from snek5000.resources import get_base_template

        template = get_base_template("compile.sh.j2")
        Output.write_compile_sh(template, config, path=output)


# create a archive with source files
# ==================================
rule source_archive:
    input:
        f"{short_name}.box",
        f"{short_name}.par",
        f"{short_name}.usr",
        "SIZE",
        "compile.sh",
        "makefile_usr.inc",
        *list(Output().makefile_usr_sources),
    output:
        f"{short_name}-source_archive.tar.gz",
    shell:
        """
        tar cvf {output} {input}
        """
```

Now execute in an IPython console to generate source code from your templates and
prescribed parameters.

```{code-cell} python
---
tags: [hide-output]
---
from phill.solver import Simul

params = Simul.create_default_params()
# modify params if necessary
sim = Simul(params)
```

Finally make the source code archive:

```{code-cell} python
---
tags: [hide-output]
---
sim.make.exec('source_archive')
```

```{code-cell} python
%mv {sim.path_run}/phill_source-archive.tar.gz .
```

This archive may now be shared to your colleagues or kept as a standalone archive which
only depends on Nek5000 for compilation.

[snek5000-phill]: https://github.com/snek5000/snek5000-phill/blob/main/src/phill/Snakefile
