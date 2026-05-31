"""Simulation container and stepping API."""

from __future__ import annotations

from dataclasses import dataclass

from astro_rt.body import Body
from astro_rt.integrators import velocity_verlet_step
from astro_rt.metrics import angular_momentum_z, total_energy


@dataclass
class SimulationSnapshot:
    """A lightweight metrics record at one instant in simulation time."""

    time: float
    energy: float
    angular_momentum_z: float


class Simulation:
    """A small simulation wrapper around bodies and integration settings.

    This is the main object that demos and tests use. It keeps the lower-level
    physics functions organized without hiding them from us while we learn.
    """

    def __init__(
        self,
        bodies: list[Body],
        dt: float = 1.0 / 365.25,
        softening: float = 0.0,
        collision_distance: float = 0.0,
    ):
        # Copy bodies so loading a scenario gives a fresh independent system.
        self.bodies = [body.copy() for body in bodies]

        # dt is the time step in years. Smaller dt is more accurate but slower.
        self.dt = dt

        # Softening can prevent extreme accelerations during near-overlaps.
        # Phase 1 keeps it at zero for exact point-mass Newtonian gravity.
        self.softening = softening
        self.collision_distance = collision_distance

        self.time = 0.0

        # Store initial metrics so demos can report drift as the sim runs.
        self.initial_energy = total_energy(self.bodies, self.softening)
        self.initial_angular_momentum_z = angular_momentum_z(self.bodies)
        self.metric_history = [self.snapshot()]

    def step(self, steps: int = 1) -> None:
        """Advance the simulation by `steps` fixed-size time steps."""

        for _ in range(steps):
            if self.collision_distance > 0.0 and self._merge_close_bodies():
                self.reset_metric_baseline()
            velocity_verlet_step(self.bodies, self.dt, self.softening)
            if self.collision_distance > 0.0 and self._merge_close_bodies():
                self.reset_metric_baseline()
            self.time += self.dt
            self._record_trails()
            self.metric_history.append(self.snapshot())

    def add_body(self, body: Body, reset_baseline: bool = True) -> None:
        """Add a new body to the running simulation.

        `reset_baseline=True` makes energy/Lz drift start from the edited
        system. Without that, the HUD would compare the new system against the
        old pre-edit system, which is not very useful for sandbox editing.
        """

        self.bodies.append(body.copy())
        if reset_baseline:
            self.reset_metric_baseline()

    def find_body(self, name: str) -> Body:
        """Return the body with `name`, or raise a clear error if missing."""

        for body in self.bodies:
            if body.name == name:
                return body
        raise ValueError(f"Unknown body: {name}")

    def remove_body(self, name: str, reset_baseline: bool = True) -> Body:
        """Remove one body from the simulation by name.

        Removing mass changes the whole gravitational system, so we usually
        reset the metric baseline after this edit.
        """

        for index, body in enumerate(self.bodies):
            if body.name == name:
                removed = self.bodies.pop(index)
                if reset_baseline:
                    self.reset_metric_baseline()
                return removed
        raise ValueError(f"Unknown body: {name}")

    def reset_metric_baseline(self) -> None:
        """Make current energy and angular momentum the new drift reference."""

        self.initial_energy = total_energy(self.bodies, self.softening)
        self.initial_angular_momentum_z = angular_momentum_z(self.bodies)
        self.metric_history = [self.snapshot()]

    def snapshot(self) -> SimulationSnapshot:
        """Measure the current state without advancing time."""

        return SimulationSnapshot(
            time=self.time,
            energy=total_energy(self.bodies, self.softening),
            angular_momentum_z=angular_momentum_z(self.bodies),
        )

    def reset_trails(self) -> None:
        """Clear stored display trails without changing physics state."""

        for body in self.bodies:
            body.trail.clear()

    def _record_trails(self, max_points: int = 1500) -> None:
        # Trails are for visualization only. We cap them so the viewer does not
        # keep growing memory forever during long runs.
        for body in self.bodies:
            body.trail.append(body.position.as_tuple())
            if len(body.trail) > max_points:
                del body.trail[: len(body.trail) - max_points]

    def _merge_close_bodies(self) -> bool:
        """Merge bodies closer than the configured collision distance.

        This is a Phase 1 guardrail for browser experiments. It prevents
        point-mass singularity fly-throughs by using a simple perfectly
        inelastic merge that conserves mass and linear momentum.
        """

        merged_any = False
        while True:
            pair: tuple[int, int] | None = None
            closest_distance = self.collision_distance

            for i in range(len(self.bodies)):
                for j in range(i + 1, len(self.bodies)):
                    distance = (self.bodies[j].position - self.bodies[i].position).norm()
                    if distance <= closest_distance:
                        pair = (i, j)
                        closest_distance = distance

            if pair is None:
                return merged_any

            i, j = pair
            self._merge_pair(i, j)
            merged_any = True

    def _merge_pair(self, first_index: int, second_index: int) -> None:
        """Replace two bodies with one mass/momentum-conserving body."""

        first = self.bodies[first_index]
        second = self.bodies[second_index]
        total_mass = first.mass + second.mass
        if total_mass <= 0.0:
            return

        position = (first.position * first.mass + second.position * second.mass) / total_mass
        velocity = (first.velocity * first.mass + second.velocity * second.mass) / total_mass
        primary = first if first.mass >= second.mass else second
        secondary = second if primary is first else first

        merged = Body(
            name=primary.name,
            mass=total_mass,
            position=position,
            velocity=velocity,
            radius=max(primary.radius, secondary.radius) + min(3.0, min(primary.radius, secondary.radius) * 0.25),
            color=primary.color,
        )

        for index in sorted((first_index, second_index), reverse=True):
            self.bodies.pop(index)
        self.bodies.append(merged)
