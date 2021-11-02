from . import pm, pv


class ReaderBase:
    @staticmethod
    def _complete_info_solver(info_solver, classes=None):
        """Static method to complete the ParamContainer info_solver.

        Parameters
        ----------

        info_solver : fluiddyn.util.paramcontainer.ParamContainer

        classes : iterable of classes

          If a class has the same tag of a default class, it replaces the
          default one (for example with the tag 'noise').

        """
        classesXML = info_solver.classes.Reader._set_child("classes")

        avail_classes = [
            pv.ReaderParaview,
            pv.ReaderParaviewStats,
            pm.ReaderPymech,
            pm.ReaderPymechStats,
        ]
        if classes is not None:
            avail_classes.extend(classes)

        for cls in avail_classes:
            classesXML._set_child(
                cls.tag,
                attribs={
                    "module_name": cls.__module__,
                    "class_name": cls.__name__,
                },
            )

    def __init__(self, sim):
        self.sim = sim
