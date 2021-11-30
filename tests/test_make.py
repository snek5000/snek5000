from concurrent.futures import ProcessPoolExecutor as Pool
from pathlib import Path


def nek5000_build(config):
    from snek5000.make import _Nek5000Make

    nm = _Nek5000Make()
    return nm.build(config)


def test_nek5000_make(pytestconfig):
    import yaml

    import snek5000
    from snek5000.output.base import Output

    if pytestconfig.getoption("--runslow"):
        # To force rebuild of Nek5000
        (Path(snek5000.get_nek_source_root()) / "bin" / "genbox").unlink()

    snek5000_config = yaml.safe_load(Output.find_configfile().read_text())

    with Pool(max_workers=4) as pool:
        # Launch simultaneous builds
        for future in (pool.submit(nek5000_build, snek5000_config) for _ in range(4)):
            assert future.result()
