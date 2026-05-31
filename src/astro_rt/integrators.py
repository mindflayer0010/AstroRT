"""Time integration methods."""

from __future__ import annotations

from astro_rt.body import Body
from astro_rt.forces import accelerations


def velocity_verlet_step(bodies: list[Body], dt: float, softening: float = 0.0) -> None:
    """Advance bodies by one Velocity-Verlet step.

    The idea:
    1. Measure acceleration from gravity right now.
    2. Move positions using current velocity and half the acceleration effect.
    3. Measure acceleration again at the new positions.
    4. Update velocity using the average of old and new acceleration.
    """

    # First gravity sample: acceleration at the start of the step.
    current_acc = accelerations(bodies, softening)

    for index, body in enumerate(bodies):
        # Position update:
        # new_position = position + velocity*dt + 0.5*acceleration*dt^2
        # This says "move because of current velocity, plus curve the path
        # because gravity is already pulling during this small time interval."
        body.position = body.position + body.velocity * dt + 0.5 * current_acc[index] * dt * dt

    # Second gravity sample: acceleration after bodies moved.
    next_acc = accelerations(bodies, softening)

    for index, body in enumerate(bodies):
        # Velocity update uses the average of old and new acceleration. That is
        # the key Velocity-Verlet trick that gives much better orbital behavior
        # than a naive Euler step.
        body.velocity = body.velocity + 0.5 * (current_acc[index] + next_acc[index]) * dt
