import snek5000


def test_get_nek_source_root():
    assert snek5000.get_nek_source_root()


def test_asset():
    assert snek5000.get_asset("nek5000.smk")
    assert snek5000.get_asset("default_configfile.yml")
