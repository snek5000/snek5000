import snek5000


def test_get_nek_source_root():
    assert snek5000.get_nek_source_root()


def test_resource():
    assert snek5000.get_snek_resource("nek5000.smk")
    assert snek5000.get_snek_resource("default_configfile.yml")
