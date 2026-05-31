"""Physical metrics used to validate the simulator."""

from __future__ import annotations

from astro_rt.body import Body
from astro_rt.constants import G
from astro_rt.vector import ZERO, Vec2


def kinetic_energy(bodies: list[Body]) -> float:
    """Energy of motion: 0.5 * mass * speed^2."""

    return sum(0.5 * body.mass * body.velocity.dot(body.velocity) for body in bodies)


def potential_energy(bodies: list[Body], softening: float = 0.0) -> float:
    """Gravitational binding energy between every pair of bodies."""

    total = 0.0
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            delta = bodies[j].position - bodies[i].position
            distance = (delta.dot(delta) + softening * softening) ** 0.5
            if distance != 0.0:
                # Potential energy is negative because gravity is attractive:
                # bound systems have less than zero total orbital energy.
                total -= G * bodies[i].mass * bodies[j].mass / distance
    return total


def total_energy(bodies: list[Body], softening: float = 0.0) -> float:
    """Total mechanical energy, used as a main simulation-health signal."""

    return kinetic_energy(bodies) + potential_energy(bodies, softening)


def angular_momentum_z(bodies: list[Body]) -> float:
    """Return the z-component of 2D angular momentum."""

    total = 0.0
    for body in bodies:
        # In 2D, angular momentum points along the z-axis:
        # Lz = m * (x*vy - y*vx).
        total += body.mass * (body.position.x * body.velocity.y - body.position.y * body.velocity.x)
    return total


def center_of_mass(bodies: list[Body]) -> Vec2:
    """Mass-weighted average position of the system."""

    total_mass = sum(body.mass for body in bodies)
    if total_mass == 0.0:
        return ZERO
    weighted = sum((body.mass * body.position for body in bodies), start=ZERO)
    return weighted / total_mass


def total_momentum(bodies: list[Body]) -> Vec2:
    """Total linear momentum of the system."""

    return sum((body.mass * body.velocity for body in bodies), start=ZERO)


def center_of_mass_velocity(bodies: list[Body]) -> Vec2:
    """Velocity of the system center of mass."""

    total_mass = sum(body.mass for body in bodies)
    if total_mass == 0.0:
        return ZERO
    return total_momentum(bodies) / total_mass


def closest_pair(bodies: list[Body]) -> tuple[str | None, str | None, float | None]:
    """Return the closest body pair and its distance."""

    if len(bodies) < 2:
        return (None, None, None)

    best_names = (None, None)
    best_distance = float("inf")
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            distance = (bodies[j].position - bodies[i].position).norm()
            if distance < best_distance:
                best_names = (bodies[i].name, bodies[j].name)
                best_distance = distance
    return (best_names[0], best_names[1], best_distance)


def relative_error(value: float, reference: float) -> float:
    """Compare drift against a starting value.

    We use this for energy and angular momentum drift because absolute changes
    can be hard to interpret across tiny and huge systems.
    """

    if reference == 0.0:
        return abs(value)
    return abs((value - reference) / reference)
