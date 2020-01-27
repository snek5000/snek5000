def test_init(oper):
    print(oper.produce_str_describing_oper())
    print(oper.produce_long_str_describing_oper())


def test_properties(oper):
    assert oper.max_n_seq == 1024
    assert oper.max_n_loc == 171


def test_box_template(oper):
    from abl.templates import box

    oper.write_box(
        box, boundary=("P", "P", "W", "W", "P", "P"), comments=__name__
    )


def test_size_template(sim):
    from abl.templates import size

    sim.oper.write_size(size, comments=__name__)
