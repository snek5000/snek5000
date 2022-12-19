# How to Jinja templates

Three files needed for Nek5000 are produced by Snek5000 through [Jinja] templates:
`<case name>.box`, `SIZE` and `makefile_usr.inc`. As a Nek5000 user, you might want to
understand how these important files are produced, so let us explain by diving into the
code:

- These files are produced by the methods:

  - {func}`snek5000.output.base.Output.write_box` (which calls
    {func}`snek5000.operators.Operators.write_box`),
  - {func}`snek5000.output.base.Output.write_size` (which calls
    {func}`snek5000.operators.Operators.write_size`) and
  - {func}`snek5000.output.base.Output.write_makefile_usr`.

- These methods are called in a method
  {func}`snek5000.output.base.Output.post_init_create_additional_source_files` which
  uses the class attributes `template_box`, `template_size` and `template_makefile_usr`.
  These attributes are defined in the solvers, for example for `snek5000-tgv` in the
  file `snek5000_tgv.output`:

  ```{eval-rst}
  .. literalinclude:: ../examples/snek5000-tgv/src/snek5000_tgv/output.py
  ```

  ```{note}
  With this mechanism, the template files can be obtained from a simulation
  object with `sim.output.template_box.filename`.
  ```

- Some base template files are in the subpackage {mod}`snek5000.resources`. These files
  are general enough so that they can be used directly by most solvers (for example we
  saw that `snek5000-tgv` uses {func}`snek5000.resources.get_base_templates`). However,
  it is also possible to use other templates. For example, in `snek5000-cbox`,
  [Jinja inheritance is used to extend the template for the `SIZE` file](https://github.com/snek5000/snek5000-cbox/tree/main/src/snek5000_cbox/templates).

[jinja]: https://jinja.palletsprojects.com
