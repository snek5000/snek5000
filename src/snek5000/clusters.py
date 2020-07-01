try:
    from fluiddyn.clusters.snic import ClusterSNIC as Base, _venv

    class Cluster(Base):
        default_project = "snic2020-1-31"
        cmd_run = "_delete"
        cmd_run_interactive = "_delete"

        def __init__(self):
            super().__init__()
            self.commands_setting_env = [
                "ml purge",
                "ml restore",
                f"source activate {_venv}",
                'export LD_LIBRARY_PATH="$LD_LIBRARY_PATH":"$LIBRARY_PATH"',
                "cd ..",
                "source activate.sh",
                "cd bin/",
            ]

        def _create_txt_launching_script(self, **kwargs):
            txt = super()._create_txt_launching_script(**kwargs)
            return "\n".join(
                [line for line in txt.splitlines() if not line.startswith("_delete")]
            )


except ImportError as e:
    from .log import logger

    logger.warning(str(e))
    logger.info("Using local machine as a cluster")
    from fluiddyn.clusters.local import ClusterLocal as Cluster  # noqa
