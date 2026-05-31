"""Body representation for the Phase 1 N-body simulator."""

from __future__ import annotations

from dataclasses import dataclass, field

from astro_rt.vector import Vec2


@dataclass
class Body:
    """A single gravitating object.

    Phase 1 intentionally keeps the state small: mass, position, velocity,
    and a few display fields. That maps cleanly to a future C++ struct/class.
    """

    # `name` is for humans and debugging; it does not affect physics.
    name: str

    # `mass` controls both how strongly this body attracts other bodies and how
    # much momentum it carries. Phase 1 uses solar masses.
    mass: float

    # `position` is where the body is now, measured in AU in Phase 1.
    position: Vec2

    # `velocity` is how fast and in which direction it is moving, measured in
    # AU/year in Phase 1.
    velocity: Vec2

    # The next three fields are display-only. They do not change gravity.
    radius: float = 4.0
    color: tuple[int, int, int] = (255, 255, 255)
    trail: list[tuple[float, float]] = field(default_factory=list)

    def copy(self) -> "Body":
        """Return an independent copy so scenarios can be reused safely."""

        return Body(
            name=self.name,
            mass=self.mass,
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            radius=self.radius,
            color=self.color,
            trail=list(self.trail),
        )
