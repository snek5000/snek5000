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
    :ref:`nek:tools_genbox`

.. literalinclude:: ../../src/snek5000/resources/box.j2
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

- ``compile.sh.j2``: See also
    :any:`snek5000.output.base.Output.write_compile_sh`.

.. literalinclude:: ../../src/snek5000/resources/compile.sh.j2
    :language: jinja

"""


import jinja2


class BaseTemplates:
    @property
    def env(self):
        return jinja2.Environment(
            loader=jinja2.PackageLoader("snek5000", "resources"),
            undefined=jinja2.StrictUndefined,
        )

    def get_base_templates(self):
        """Get templates (box, makefile_usr and size) from ``snek5000.resources``."""
        box = self.env.get_template("box.j2")
        makefile_usr = self.env.get_template("makefile_usr.inc.j2")
        size = self.env.get_template("SIZE.j2")
        return box, makefile_usr, size

    def get_base_template(self, name):
        """Get a template from ``snek5000.resources``."""
        return self.env.get_template(name)


_templates = BaseTemplates()

get_base_templates = _templates.get_base_templates
get_base_template = _templates.get_base_template
