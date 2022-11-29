"""resources for building
======================

Contains common snakemake rules and jinja templates.

Snakemake rules
---------------

- ``nek5000.smk``: subworkflow_ for building Nek5000 tools

.. literalinclude:: ../../src/snek5000/resources/nek5000.smk
    :language: python

- ``compiler.smk``: module_ for compiling user code

.. literalinclude:: ../../src/snek5000/resources/compiler.smk
    :language: python

- ``io.smk``: module_ for cleaning and archiving simulation artefacts

.. literalinclude:: ../../src/snek5000/resources/io.smk
    :language: python

- ``internal.smk``: module_ for generating simulation files, serves as inputs
  to Snakemake rules above

.. literalinclude:: ../../src/snek5000/resources/internal.smk
    :language: python

.. _module: https://snakemake.readthedocs.io/en/stable/snakefiles/modularization.html#modules
.. _subworkflow: https://snakemake.readthedocs.io/en/stable/snakefiles/modularization.html#sub-workflows


Jinja templates
---------------

- ``box.j2``: See also
    :any:`snek5000.operators.Operators.write_box`,
    :any:`snek5000.output.base.Output.write_box`.
    :ref:`nek:mesh_gen`

.. literalinclude:: ../../src/snek5000/resources/box.j2
    :language: jinja

- ``compile.sh.j2``: See also
    :any:`snek5000.output.base.Output.write_compile_sh`.

.. literalinclude:: ../../src/snek5000/resources/compile.sh.j2
    :language: jinja

- ``makefile_usr.inc.j2``: See also
    :any:`snek5000.output.base.Output.write_makefile_usr`.

.. literalinclude:: ../../src/snek5000/resources/makefile_usr.inc.j2
    :language: jinja

- ``SIZE.j2``: See also
    :any:`snek5000.operators.Operators.write_size`,
    :any:`snek5000.output.base.Output.write_size`,
    Nek5000 docs on :ref:`nek:case_files_size` file.

.. literalinclude:: ../../src/snek5000/resources/SIZE.j2
    :language: jinja

"""
