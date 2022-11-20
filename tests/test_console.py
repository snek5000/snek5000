from snek5000.util.console import print_versions, start_ipython_load_sim


def test_info():
    print_versions()


def test_start_ipython_load_sim(mocker):
    mocker.patch("IPython.start_ipython")
    start_ipython_load_sim()
