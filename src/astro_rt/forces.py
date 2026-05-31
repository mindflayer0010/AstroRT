"""Force and acceleration calculations."""

from __future__ import annotations

from astro_rt.body import Body
from astro_rt.constants import G
from astro_rt.vector import ZERO, Vec2


def accelerations(bodies: list[Body], softening: float = 0.0) -> list[Vec2]:
    """Return gravitational acceleration for each body.

    The direct pairwise method is O(N^2): every body checks every other body.
    That is perfect for Phase 1 because it is simple and physically transparent.
    Barnes-Hut and learned approximations come later.
    """

    count = len(bodies)

    # Each entry in `acc` is the total acceleration acting on the body with the
    # same index. We accumulate contributions from every other body.
    acc = [ZERO for _ in bodies]

    for i in range(count):
        # Start at i + 1 so each pair is handled once: (Sun, Earth), not both
        # (Sun, Earth) and (Earth, Sun). We update both bodies inside the loop.
        for j in range(i + 1, count):
            # delta points from body i toward body j. This gives the direction
            # of the gravitational pull on body i.
            delta = bodies[j].position - bodies[i].position

            # Softening is a future safety tool for close encounters. At 0.0 we
            # use exact Newtonian point-mass gravity.
            distance_sq = delta.dot(delta) + softening * softening
            distance = distance_sq**0.5

            # If two bodies occupy the exact same point, the Newtonian formula
            # would divide by zero. Later collision handling should catch this.
            if distance == 0.0:
                continue

            # Vector gravity uses delta / |delta|^3. That is equivalent to
            # "direction / distance^2" but avoids separately normalizing delta.
            direction_over_r2 = delta / (distance_sq * distance)

            # Acceleration on i depends on mass of j. Acceleration on j depends
            # on mass of i in the opposite direction. This preserves the
            # equal-and-opposite pair interaction.
            acc[i] += G * bodies[j].mass * direction_over_r2
            acc[j] -= G * bodies[i].mass * direction_over_r2

    return acc
