from io import StringIO


def test_init(oper):
    print(oper.produce_str_describing_oper())
    print(oper.produce_long_str_describing_oper())


def test_properties(oper):
    assert oper.max_n_seq == 1024
    assert oper.max_n_loc == 171


def test_box_template(oper, jinja_env, datadir):
    box = jinja_env.get_template("box.j2")
    expected = (datadir / "test_box_template.box").read_text()

    with StringIO() as buffer:
        oper.write_box(box, fp=buffer, comments=__name__)
        assert buffer.getvalue() == expected


def test_box_2d(oper2d, jinja_env, datadir):
    box = jinja_env.get_template("box.j2")
    expected = (datadir / "test_box_2d.box").read_text()

    with StringIO() as buffer:
        oper2d.write_box(box, fp=buffer, comments=__name__)
        assert buffer.getvalue() == expected


def test_size_template(sim, jinja_env, datadir):
    size = jinja_env.get_template("SIZE.j2")
    expected = (datadir / "test_size_template.f").read_text()

    with StringIO() as buffer:
        sim.oper.write_size(size, fp=buffer, comments=__name__)
        assert buffer.getvalue().splitlines() == expected.splitlines()


def test_size_2d(sim2d, jinja_env, datadir):
    size = jinja_env.get_template("SIZE.j2")
    expected = (datadir / "test_size_2d.f").read_text()

    with StringIO() as buffer:
        sim2d.oper.write_size(size, fp=buffer, comments=__name__)
        assert buffer.getvalue().splitlines() == expected.splitlines()


def test_sim_path_run(sim):
    params = sim.params
    assert params.oper.Lx == params.oper.Ly == params.oper.Lz == 1.0
    assert sim.oper.produce_str_describing_oper() in sim.name_run
