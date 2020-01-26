def test_init(oper):
    print(oper.produce_str_describing_oper())
    print(oper.produce_long_str_describing_oper())


def test_properties(oper):
    params = oper.params
    params.oper.nx = params.oper.ny = params.oper.nz = 9
    params.oper.nproc_min = 6

    assert oper.max_n_seq == 1024
    assert oper.max_n_loc == 171
