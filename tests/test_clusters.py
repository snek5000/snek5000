from snek5000.clusters import nproc_available


def test_nproc_available():
    nproc = nproc_available()
    assert nproc > 0
    assert isinstance(nproc, int)
