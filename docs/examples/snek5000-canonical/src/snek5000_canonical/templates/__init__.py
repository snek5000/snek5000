import jinja2

env = jinja2.Environment(
    loader=jinja2.PackageLoader("snek5000", "assets"),
    #  loader=jinja2.PackageLoader("snek5000_canonical", "templates"),
    undefined=jinja2.StrictUndefined,
)

box = env.get_template("box.j2")
size = env.get_template("SIZE.j2")
makefile_usr = env.get_template("makefile_usr.inc.j2")
