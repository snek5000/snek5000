"""Operators classes
====================

Information regarding mesh, mathematical operators, and domain decomposition.

.. todo:: Generate SIZE and abl.box files (using sympy.codegen, jinja or
          str.template)

.. todo:: Move length to abl.par file and extrude it to allow double precision
          values.

.. note:: We deliberately try not to use the variable names used in Nek5000, as
          those are ambiguously named.

"""
import math
import sys
from math import pi
from .util import docstring_params


def _str_len(length):
    """Generates a special string if length is multiple of pi. If not provide 3
    decimal places past floating point.

    """
    if (length / pi).is_integer():
        str_len = repr(int(length / pi)) + "pi"
    else:
        str_len = f"{length:.3f}".rstrip("0")

    return str_len


def next_power(value, base=2):
    """Compute the perfect power of ``base`` greater than or equal to ``value``.

    :param value:
    :type value: int or float

    :param int base:

    :return int:

    """
    exponent = math.ceil(math.log(value, base))
    return base ** exponent


class Operators:
    """Container for parameters and writing box_ and SIZE_ files.

    .. _box: https://nek5000.github.io/NekDoc/appendix.html?\
#generating-a-mesh-with-genbox
    .. _SIZE: https://nek5000.github.io/NekDoc/problem_setup/case_files.html\
#size

    .. note:: Some values are not available as parameters and instead
              automatically computed for generating the SIZE file.

    ==============  ===================   =====================================
    SIZE            `properties`          Comment
    ==============  ===================   =====================================
    ``lelg``        ``max_n_seq``         Max. number of elements globally
    ``lelt``        ``max_n_loc``         | Max. number of elements per
                                            processor (should be not smaller
                                          | than ``lelg/lpmin``, i.e.

    ``lelx``        None                  | **Automatically computed**. Max.
                                            number of elements along x
                                          | direction for the global tensor
                                            product solver / dimensions.

    ``lely``        None                  Same as above for ``y`` direction.
    ``lelz``        None                  Same as above for ``z`` direction.

    ``lbelt``       None                  | **Automatically computed** as
                                          |  ``lelt`` if ``"MHD" in
                                            params.nek.problem_type.equation``.
    ``lpelt``       None                  | **Automatically computed** as
                                          |  ``lelt`` if ``"linear" in
                                            params.nek.problem_type.equation``.
    ``lcvelt``      None                  | **Automatically computed** as
                                          |  ``lelt`` if
                                            ``params.nek.cvode._enabled is
                                            True``

    ``lx1m``        None                  | p-order for mesh solver.
                                            **Automatically computed** from
                                          | ``params.nek.general.stressFormulat\
ion``
    ==============  ===================   =====================================

    """

    @staticmethod
    def _complete_params_with_default(params):
        """This static method is used to complete the *params* container.
        """
        attribs = {
            "nx": 48,
            "ny": 48,
            "nz": 48,
            "Lx": 2 * pi,
            "Ly": 2 * pi,
            "Lz": 2 * pi,
            "dim": 3,
            "nproc_min": 8,
            "nproc_max": 32,
            "scalars": 1,
        }
        params._set_child("oper", attribs=attribs)
        params.oper._set_doc(
            """

The following table matches counterpart of mandatory ``SIZE`` variables.

==========  ===================   =============================================
SIZE        params.oper           Comment
==========  ===================   =============================================
``ldim``    ``dim``               Domain dimensions (2 or 3)

``lpmin``   ``nproc_min``         Min MPI ranks
``lpmax``   ``nproc_max``         Max MPI ranks
``ldimt``   ``scalars``           Number of auxilary fields (minimum 1).
==========  ===================   =============================================

"""
        )

        attribs = {
            option: 1
            for option in (
                "dim_krylov",
                "dim_proj",
                "hist",
                "obj",
                "perturb",
                "scalars_cons",
                "scalars_proj",
                "sessions",
            )
        }
        attribs["order_time"] = 2

        params.oper._set_child("max", attribs=attribs)
        params.oper.max._set_doc(
            """
The following table matches counterpart of optional ``SIZE`` variables. These
refer to upper bound number of `something`. The parameters are considered
"optional" and would be ignored with the default values.

==============  ===================   =========================================
SIZE            params.oper.max       Comment
==============  ===================   =========================================
``mxprev``      ``dim_proj``          Max. dimension of projection space
``lgmres``      ``dim_krylov``        Max. dimension of Krylov space for GMRES
``lhis``        ``hist``              Max. number of history (i.e. monitoring)
                                      points.

``maxobj``      ``obj``               Max. number of objects?
``lorder``      ``order_time``        Max. temporal order (minimum: 2)
``lpert``       ``perturb``           Max. number of perturbations
``toteq``       ``scalars_cons``      Max. conserved scalars
``ldimt_proj``  ``scalars_proj``      Max. scalars for residual projection
``nsessmax``    ``sessions``          Max. sessions to NEKNEK

==============  ===================   =========================================
"""
        )

        attribs = {
            "order": 6,
            "order_out": 6,
            "coef_dealiasing": 2.0 / 3,
            "staggered": True,
        }
        params.oper._set_child("elem", attribs=attribs)
        params.oper.elem._set_doc(
            r"""
The following table relate to element configuration for certain operations.
The parameters are considered "optional" (except for ``lx1`` / ``order`` and
``lxd`` / ``coef_dealiasing`` which are mandatory) and would be ignored with
the default values.

==========      ===================   =========================================
SIZE            params.oper.elem      Comment
==========      ===================   =========================================
``lxd``         ``coef_dealiasing``   | p-order for over-integration.
                                        **Automatically computed** from float
                                      | ``coef_dealiasing``.

``lx1``         ``order``             p-order (avoid uneven and values <6).

``lxo``         ``order_out``         Max. p-order on output (should be ``>=
                                      order``)

``lx2``         ``staggered``         | p-order for pressure. **Automatically
                                        computed** from boolean
                                      | ``staggered`` (`True` implies
                                        :math:`\mathbb{P}_N - \mathbb{P}_{N-2}`
                                        and `False` implies :math:`\mathbb{P}_N
                                        - \mathbb{P}_{N}` or a collocated grid).

==========      ===================   =========================================

.. _[#p-order] Polynomial order. Number of GLL points per element.

"""
        )

    def __init__(self, sim=None, params=None):
        self.params = sim.params if sim else params
        self.axes = ("x", "y", "z")

    @property
    def max_n_seq(self):
        params = self.params
        return next_power(params.oper.nx * params.oper.ny * params.oper.nz)

    @property
    def max_n_loc(self):
        """The next integer greater than or equals ``max_n_seq /
        params.oper.nproc_min``.
        """
        return math.ceil(self.max_n_seq / self.params.oper.nproc_min)

    @property
    def nb_fields(self):
        return self.params.oper.scalars + 1

    def memory_required(self):
        """According to FAQ_ the following estimate::

            lx1*ly1*lz1*lelt * 3000byte + lelg * 12byte + MPI + optional libraries
            (e.g. CVODE)

        .. _FAQ: https://nek5000.github.io/NekDoc/faq.html?highlight=memory

        """
        params = self.params
        elem = params.oper.elem

        lx1 = elem.order
        ldim = params.oper.ndim
        ly1 = lx1
        lz1 = 1 + (ldim - 2) * (lx1 - 1)
        lelt = self.max_n_loc
        lelg = self.max_n_seq

        return lx1 * ly1 * lz1 * lelt * 3000 + lelg * 12

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

    def write_box(self, template, boundary, fp=sys.stdout, comments=""):
        """Write the .box file which is input for the ``genbox`` meshing
        tool.

        :param jinja2.environment.Template template: Template instance like
            :ref:``abl.templates.box``

        :param boundary: Boundary conditions
        :type boundary: tuple[str]

        :param fp: File pointer to write to

        """
        params = self.params
        comments += """
Autogenerated using eturb.operators.write_box()

If dim < 0 .re2 file will be generated

If nelx (y or z) < 0, then genbox automatically generates the
                      grid spacing in the x (y or z) direction
                      with a geometric ratio given by "ratio".
                      ( ratio=1 implies uniform spacing )

Note that the character bcs _must_ have 3 spaces.
"""

        def _str_grid(*args):
            fmt = "{:.1f} {:.4f} {:.1f}"
            args = (float(value) for value in args)
            return fmt.format(*args)

        for bc in boundary:
            if len(bc) > 3:
                raise ValueError(
                    f"Length of boundary condition {bc} shall not exceed 3 characters"
                )

        # A dictionary mapping a comment to grid
        grid_info = {
            "nelx nely nelz": " ".join(
                str(-n) for n in (params.oper.nx, params.oper.ny, params.oper.nz)
            ),
            "x0 x1 ratio": _str_grid(0, params.oper.Lx, 1),
            "y0 y1 ratio": _str_grid(0, params.oper.Ly, 1),
            "z0 z1 ratio": _str_grid(0, params.oper.Lz, 1),
            "BCs: (cbx0, cbx1, cby0, cby1, cbz0, cbz1)": ",".join(
                bc.ljust(3) for bc in boundary
            ),
        }
        options = {
            "dim": str(-params.oper.dim),
            "nb_fields": str(self.nb_fields),  # scalars + velocity
            "comments": comments,
            "grid_info": grid_info,
        }

        output = template.render(**options)
        fp.write(output)

    def write_size(self, template, fp=sys.stdout):
        """Write the SIZE file which is required for compilation.

        :param jinja2.environment.Template template: Template instance like
            :ref:``abl.templates.size``

        """
        pass


__doc__ += docstring_params(Operators)
