from eturb.params import Parameters


def test_write():
    params = Parameters("test_case")
    params.write_par()
