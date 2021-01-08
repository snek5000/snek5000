import pytest

try:
    from IPython.testing.globalipapp import get_ipython

    ip = get_ipython()
    ip.magic("load_ext snek5000.magic")
except ImportError:
    ip = False


@pytest.mark.skipif(not ip, reason="Magics cannot be tested if IPython is unavailable")
def test_snek5000_magic():
    ip.run_line_magic("snek", "kth")
