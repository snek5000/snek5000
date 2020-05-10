import snek5000


def test_nek5000():
    assert snek5000.source_root()


def test_asset():
    assert snek5000.get_asset("nek5000.smk")
    assert snek5000.get_asset("default_configfile.yml")
