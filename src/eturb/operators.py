from math import pi


def _str_len(length):
    if (length / pi).is_integer():
        str_len = repr(int(length / pi)) + "pi"
    else:
        str_len = f"{length:.3f}".rstrip("0")

    return str_len


class Operators:
    """Container for parameters regarding mesh.

    .. todo:: Template for box file required mesh generation

    """

    @staticmethod
    def _complete_params_with_default(params):
        """This static method is used to complete the *params* container.
        """
        attribs = {
            "coef_dealiasing": 2.0 / 3,
            "nx": 48,
            "ny": 48,
            "nz": 48,
            "Lx": 2 * pi,
            "Ly": 2 * pi,
            "Lz": 2 * pi,
        }
        params._set_child("oper", attribs=attribs)

    def __init__(self, sim=None, params=None):
        self.params = sim.params if sim else params
        self.axes = ("x", "y", "z")

    def _str_Ln(self):
        params = self.params.oper
        str_L = map(_str_len, (params.Lx, params.Ly, params.Lz))
        str_n = map(str, (params.nx, params.ny, params.nz))
        return str_L, str_n

    def produce_str_describing_oper(self):
        """Produce a string describing the operator."""
        str_L, str_n = self._str_Ln()
        return f"{'x'.join(str_n)}_V{'x'.join(str_L)}"

    def produce_long_str_describing_oper(self, oper_method="Base"):
        """Produce a string describing the operator."""
        str_L, str_n = self._str_Ln()
        string = ""
        for key, value in zip(("Lx", "Ly", "Lz"), str_L):
            string += f"- {key} = {value}\n"
        for key, value in zip(("nx", "ny", "nz"), str_n):
            string += f"- {key} = {value}\n"
        return f"Nek5000 operator:\n{string}"
