"""Calculate physical constants"""
import math


def coriolis_freq(lat):
    """Compute coriolis frequency.

    https://en.wikipedia.org/wiki/Earth%27s_rotation#Angular_speed
    omega = 7.2921150 ± 0.0000001×10−5 radians per second

    :param theta: Latitude in degrees.

    """
    omega = 7.2921150e-5
    theta = math.radians(lat)
    f = 2 * omega * math.sin(theta)
    return f
