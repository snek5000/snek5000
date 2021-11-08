"""Calculate physical constants"""
import math


def coriolis_freq(lat):
    r"""Compute coriolis frequency in the f-plane.

    .. math::

        \omega &= 7.2921150 ± 0.0000001×10^{−5} \, \text{radians per second} \\
        f &= 2 \omega \sin(\theta)


    .. seealso::
        https://en.wikipedia.org/wiki/Earth%27s_rotation#Angular_speed

    Parameters
    ----------
    lat: float
        Latitude in degrees, which gets converted to radians :math:`\theta`.

    Returns
    -------
    f: float
        Coriolis frequency in radians per second

    """
    omega = 7.2921150e-5
    theta = math.radians(lat)
    f = 2 * omega * math.sin(theta)
    return f
