"""Small orbital mechanics helpers for Phase 1.

These formulas are two-body approximations. AstroRT still advances the full
system with N-body gravity after the initial velocity is chosen.
"""

from __future__ import annotations

from math import pi, sqrt

from astro_rt.constants import G


def gravitational_parameter(central_mass: float, orbiting_mass: float) -> float:
    """Return mu = G * (M + m) for a two-body system."""

    return G * (central_mass + orbiting_mass)


def circular_speed(central_mass: float, orbiting_mass: float, radius: float) -> float:
    """Return speed needed for a circular orbit at `radius`."""

    if radius <= 0.0:
        raise ValueError("radius must be positive")
    return sqrt(gravitational_parameter(central_mass, orbiting_mass) / radius)


def escape_speed(central_mass: float, orbiting_mass: float, radius: float) -> float:
    """Return local escape speed at `radius`."""

    if radius <= 0.0:
        raise ValueError("radius must be positive")
    return sqrt(2.0 * gravitational_parameter(central_mass, orbiting_mass) / radius)


def elliptical_speed(central_mass: float, orbiting_mass: float, radius: float, semi_major_axis: float) -> float:
    """Return orbital speed from the vis-viva equation."""

    if radius <= 0.0:
        raise ValueError("radius must be positive")
    if semi_major_axis <= 0.0:
        raise ValueError("semi-major axis must be positive")
    term = 2.0 / radius - 1.0 / semi_major_axis
    if term < 0.0:
        raise ValueError("orbit is not bound at this radius and semi-major axis")
    return sqrt(gravitational_parameter(central_mass, orbiting_mass) * term)


def periapsis_speed(central_mass: float, orbiting_mass: float, periapsis: float, apoapsis: float) -> float:
    """Return speed at periapsis for an elliptical orbit."""

    if periapsis <= 0.0 or apoapsis <= 0.0:
        raise ValueError("periapsis and apoapsis must be positive")
    semi_major_axis = 0.5 * (periapsis + apoapsis)
    return elliptical_speed(central_mass, orbiting_mass, periapsis, semi_major_axis)


def periapsis_speed_from_eccentricity(
    central_mass: float,
    orbiting_mass: float,
    periapsis: float,
    eccentricity: float,
) -> float:
    """Return periapsis speed when the current radius is periapsis."""

    if periapsis <= 0.0:
        raise ValueError("periapsis must be positive")
    bounded_eccentricity = max(0.0, min(0.95, eccentricity))
    return sqrt(
        gravitational_parameter(central_mass, orbiting_mass)
        * (1.0 + bounded_eccentricity)
        / periapsis
    )


def orbital_period(central_mass: float, orbiting_mass: float, semi_major_axis: float) -> float:
    """Return the period of a bound two-body orbit in years."""

    if semi_major_axis <= 0.0:
        raise ValueError("semi-major axis must be positive")
    return 2.0 * pi * sqrt(semi_major_axis**3 / gravitational_parameter(central_mass, orbiting_mass))
