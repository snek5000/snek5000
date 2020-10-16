"""Assets for building
======================

Contains common snakemake rules and jinja templates.

Snakemake rules
---------------

- ``nek5000.smk``

.. literalinclude:: ../../src/snek5000/assets/nek5000.smk
    :language: python


Jinja templates
---------------

- ``box.j2``: See also
    :any:`snek5000.operators.Operators.write_box`,
    :any:`snek5000.output.base.Output.write_box`.

.. literalinclude:: ../../src/snek5000/assets/box.j2

- ``makefile_usr.inc.j2``: See also
    :any:`snek5000.output.base.Output.write_makefile_usr`.

.. literalinclude:: ../../src/snek5000/assets/makefile_usr.inc.j2

- ``SIZE.j2``: See also
    :any:`snek5000.operators.Operators.write_size`,
    :any:`snek5000.output.base.Output.write_size`.

.. literalinclude:: ../../src/snek5000/assets/SIZE.j2


"""
