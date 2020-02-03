"""ABL solver
=============

A solver which specifically deals with the ABL case files.

"""
from abl import get_root, templates

from .. import logger, mpi
from ..info import InfoSolverABL
from ..util import docstring_params
from .kth import SimulKTH


class SimulABL(SimulKTH):
    """ABL solver. Write box and SIZE files on initialization.

    """

    InfoSolver = InfoSolverABL

    @staticmethod
    def _complete_params_with_default(params):
        params = SimulKTH._complete_params_with_default(params)

        # Synchronize baseline parameters
        primary_par_file = get_root() / "abl.par"
        if mpi.rank == 0:
            logger.info(f"Reading baseline parameters from {primary_par_file}")

        params.nek._read_par(primary_par_file)
        params.nek._set_doc(
            f"Default parameters are overriden by {primary_par_file.name}"
        )
        for child in params.nek._tag_children:
            param_child = getattr(params.nek, child)
            param_child._set_doc("")
            param_child._autodoc_par()
        return params

    def __init__(self, params):
        super().__init__(params)
        if mpi.rank == 0:
            box_file = self.path_run / f"{self.output.name_pkg}.box"
            logger.info(f"Writing box file... {box_file}")
            with open(box_file, "w") as fp:
                self.oper.write_box(
                    templates.box, fp, comments=params.short_name_type_run
                )

            size_file = self.path_run / "SIZE"
            logger.info(f"Writing SIZE file... {size_file}")
            with open(size_file, "w") as fp:
                self.oper.write_size(
                    templates.size, fp, comments=params.short_name_type_run
                )


Simul = SimulABL
Simul.__doc__ += "\n" + docstring_params(Simul, indent_len=4)
