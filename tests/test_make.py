def test_nek5000_make():
    import yaml

    from snek5000.make import _Nek5000Make
    from snek5000.output.base import Output

    config = yaml.safe_load(Output.find_configfile().read_text())
    nm = _Nek5000Make()
    assert nm.build(config)
