"""Repeatable starting systems for demos and tests."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

from astro_rt.body import Body
from astro_rt.orbits import periapsis_speed
from astro_rt.vector import vec2

# Earth is tiny compared with the Sun. Keeping this realistic mass ratio makes
# the Sun-Earth demo physically meaningful while still easy to inspect.
EARTH_MASS_IN_SOLAR_MASSES = 3.003e-6
MARS_MASS_IN_SOLAR_MASSES = 3.227e-7


@dataclass(frozen=True)
class ScenarioInfo:
    """Human-facing notes and numerical hints for one scenario."""

    label: str
    stability: str
    note: str
    dt_scale: float = 1.0
    softening: float = 0.0


def blank() -> list[Body]:
    """Empty workspace for building a system from scratch."""

    return []


def single_sun() -> list[Body]:
    """A clean central star workspace for adding orbiting bodies."""

    return [Body("Sun", 1.0, vec2(0.0, 0.0), vec2(0.0, 0.0), 10, (255, 215, 0))]


def sun_earth() -> list[Body]:
    """A near-circular one-year Earth orbit around the Sun."""

    return [
        Body(
            name="Sun",
            mass=1.0,
            position=vec2(0.0, 0.0),
            # Give the Sun a tiny opposite velocity so total momentum starts
            # closer to balanced instead of pinning the Sun completely still.
            velocity=vec2(0.0, -EARTH_MASS_IN_SOLAR_MASSES * 2.0 * pi),
            radius=10,
            color=(255, 215, 0),
        ),
        Body(
            name="Earth",
            mass=EARTH_MASS_IN_SOLAR_MASSES,
            position=vec2(1.0, 0.0),
            # In our normalized units, 2*pi AU/year is the circular speed at
            # 1 AU around a 1 solar-mass star.
            velocity=vec2(0.0, 2.0 * pi),
            radius=5,
            color=(90, 160, 255),
        ),
    ]


def sun_earth_elliptical() -> list[Body]:
    """Earth-like body started at perihelion with real-ish eccentricity."""

    # Earth's real eccentricity is about 0.0167. These perihelion/aphelion
    # distances are rounded AU values, enough to show an ellipse in Phase 1.
    perihelion = 0.9833
    aphelion = 1.0167
    speed = periapsis_speed(1.0, EARTH_MASS_IN_SOLAR_MASSES, perihelion, aphelion)
    return [
        Body(
            name="Sun",
            mass=1.0,
            position=vec2(0.0, 0.0),
            velocity=vec2(0.0, -EARTH_MASS_IN_SOLAR_MASSES * speed),
            radius=10,
            color=(255, 215, 0),
        ),
        Body(
            name="Earth-e",
            mass=EARTH_MASS_IN_SOLAR_MASSES,
            position=vec2(perihelion, 0.0),
            velocity=vec2(0.0, speed),
            radius=5,
            color=(90, 180, 255),
        ),
    ]


def binary_stars() -> list[Body]:
    """Two equal-mass stars orbiting their shared center of mass."""

    # With two 0.5 solar-mass stars separated by 1 AU, each star orbits at
    # radius 0.5 AU. speed=pi gives the circular solution in our units.
    speed = pi
    return [
        Body("Star A", 0.5, vec2(-0.5, 0.0), vec2(0.0, -speed), 8, (255, 200, 120)),
        Body("Star B", 0.5, vec2(0.5, 0.0), vec2(0.0, speed), 8, (120, 190, 255)),
    ]


def inner_solar_system() -> list[Body]:
    """Simple circular-orbit approximation of Mercury through Mars."""

    return [
        Body("Sun", 1.0, vec2(0.0, 0.0), vec2(0.0, 0.0), 10, (255, 215, 0)),
        # Speeds use v = 2*pi / sqrt(r), the circular-orbit speed around a
        # one-solar-mass Sun at radius r AU.
        Body("Mercury", 1.651e-7, vec2(0.387, 0.0), vec2(0.0, 2.0 * pi / sqrt(0.387)), 3, (180, 180, 180)),
        Body("Venus", 2.447e-6, vec2(0.723, 0.0), vec2(0.0, 2.0 * pi / sqrt(0.723)), 4, (220, 180, 120)),
        Body("Earth", EARTH_MASS_IN_SOLAR_MASSES, vec2(1.0, 0.0), vec2(0.0, 2.0 * pi), 5, (90, 160, 255)),
        Body("Mars", 3.227e-7, vec2(1.524, 0.0), vec2(0.0, 2.0 * pi / sqrt(1.524)), 4, (220, 90, 60)),
    ]


def elliptical_inner_solar_system() -> list[Body]:
    """Simple perihelion starts using real-ish eccentricity for inner planets."""

    planets = [
        # name, mass, perihelion AU, aphelion AU, radius, color
        ("Mercury-e", 1.651e-7, 0.3075, 0.4667, 3, (180, 180, 180)),
        ("Venus-e", 2.447e-6, 0.7184, 0.7282, 4, (220, 180, 120)),
        ("Earth-e", EARTH_MASS_IN_SOLAR_MASSES, 0.9833, 1.0167, 5, (90, 160, 255)),
        ("Mars-e", MARS_MASS_IN_SOLAR_MASSES, 1.3814, 1.6660, 4, (220, 90, 60)),
    ]
    bodies = [Body("Sun", 1.0, vec2(0.0, 0.0), vec2(0.0, 0.0), 10, (255, 215, 0))]
    for name, mass, perihelion, aphelion, radius, color in planets:
        bodies.append(
            Body(
                name,
                mass,
                vec2(perihelion, 0.0),
                vec2(0.0, periapsis_speed(1.0, mass, perihelion, aphelion)),
                radius,
                color,
            )
        )
    return bodies


def comet_sun() -> list[Body]:
    """A high-eccentricity comet-like orbit that makes the ellipse obvious."""

    perihelion = 0.35
    aphelion = 4.5
    comet_mass = 1.0e-12
    return [
        Body("Sun", 1.0, vec2(0.0, 0.0), vec2(0.0, 0.0), 10, (255, 215, 0)),
        Body(
            "Comet",
            comet_mass,
            vec2(perihelion, 0.0),
            vec2(0.0, periapsis_speed(1.0, comet_mass, perihelion, aphelion)),
            3,
            (170, 245, 255),
        ),
    ]


def sun_jupiter() -> list[Body]:
    """A cleaner two-body giant-planet scenario for visible barycenter motion."""

    jupiter_mass = 9.545e-4
    radius = 5.204
    speed = 2.0 * pi / sqrt(radius)
    return [
        Body("Sun", 1.0, vec2(0.0, 0.0), vec2(0.0, -jupiter_mass * speed), 10, (255, 215, 0)),
        Body("Jupiter", jupiter_mass, vec2(radius, 0.0), vec2(0.0, speed), 7, (230, 170, 120)),
    ]


def three_body_lab() -> list[Body]:
    """A deliberately non-realistic three-body setup for chaotic experiments."""

    return [
        Body("A", 1.0, vec2(-0.8, 0.0), vec2(0.0, -1.15), 7, (255, 190, 120)),
        Body("B", 1.0, vec2(0.8, 0.0), vec2(0.0, 1.15), 7, (120, 190, 255)),
        Body("C", 0.15, vec2(0.0, 0.9), vec2(-2.3, 0.0), 5, (160, 245, 180)),
    ]


SCENARIOS = {
    "blank": blank,
    "single_sun": single_sun,
    "sun_earth": sun_earth,
    "sun_earth_elliptical": sun_earth_elliptical,
    "comet_sun": comet_sun,
    "binary_stars": binary_stars,
    "sun_jupiter": sun_jupiter,
    "three_body_lab": three_body_lab,
    "inner_solar_system": inner_solar_system,
    "elliptical_inner_solar_system": elliptical_inner_solar_system,
}

SCENARIO_INFO = {
    "blank": ScenarioInfo("Blank", "stable", "Empty workspace for building from scratch."),
    "single_sun": ScenarioInfo("Single Star", "stable", "Clean central-star workspace."),
    "sun_earth": ScenarioInfo("Sun-Earth", "stable", "Circular validation orbit with excellent energy behavior."),
    "sun_earth_elliptical": ScenarioInfo("Earth Ellipse", "stable", "Earth-like eccentricity; the ellipse is physically subtle."),
    "binary_stars": ScenarioInfo("Binary Stars", "stable", "Two equal stars in a clean shared orbit."),
    "sun_jupiter": ScenarioInfo("Sun-Jupiter", "stable", "Giant-planet two-body setup with visible scale separation."),
    "inner_solar_system": ScenarioInfo("Inner Solar", "stable", "Circular inner-planet validation scenario."),
    "elliptical_inner_solar_system": ScenarioInfo(
        "Inner Solar Ellipse",
        "sensitive",
        "Real-ish eccentric starts; smaller timesteps improve long-run drift.",
    ),
    "comet_sun": ScenarioInfo(
        "Comet",
        "sensitive",
        "High-eccentricity orbit; fast periapsis motion needs smaller timesteps.",
        dt_scale=0.25,
    ),
    "three_body_lab": ScenarioInfo(
        "3-Body Lab",
        "chaotic",
        "Close-encounter chaotic lab; uses softening and smaller timesteps for display stability.",
        dt_scale=0.25,
        softening=0.03,
    ),
}


def scenario_info(name: str) -> ScenarioInfo:
    """Return metadata/hints for a scenario."""

    return SCENARIO_INFO.get(name, ScenarioInfo(name.replace("_", " "), "custom", "User-loaded custom system."))


def load_scenario(name: str) -> list[Body]:
    """Build a fresh scenario by name.

    Returning new bodies each time matters because simulations mutate body
    positions and velocities as they run.
    """

    try:
        return SCENARIOS[name]()
    except KeyError as exc:
        choices = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"Unknown scenario {name!r}. Choices: {choices}") from exc
