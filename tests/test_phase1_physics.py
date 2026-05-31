from __future__ import annotations

import math
import unittest

from astro_rt.forces import accelerations
from astro_rt.metrics import angular_momentum_z, center_of_mass, relative_error, total_energy
from astro_rt.orbits import circular_speed, escape_speed, orbital_period, periapsis_speed
from astro_rt.scenarios import load_scenario
from astro_rt.simulation import Simulation


class Phase1PhysicsTests(unittest.TestCase):
    def test_sun_earth_energy_and_angular_momentum_stay_small_after_one_orbit(self) -> None:
        sim = Simulation(load_scenario("sun_earth"), dt=1.0 / 365.25)
        initial_energy = total_energy(sim.bodies)
        initial_lz = angular_momentum_z(sim.bodies)

        sim.step(366)

        self.assertLess(relative_error(total_energy(sim.bodies), initial_energy), 1e-6)
        self.assertLess(relative_error(angular_momentum_z(sim.bodies), initial_lz), 1e-12)

    def test_earth_returns_near_starting_position_after_one_year(self) -> None:
        sim = Simulation(load_scenario("sun_earth"), dt=1.0 / 365.25)
        earth_start = sim.bodies[1].position.copy()

        sim.step(366)

        earth_end = sim.bodies[1].position
        self.assertLess((earth_end - earth_start).norm(), 0.03)

    def test_pairwise_acceleration_respects_newtons_third_law_in_mass_weighted_form(self) -> None:
        bodies = load_scenario("sun_earth")
        acc = accelerations(bodies)

        total_force_like = bodies[0].mass * acc[0] + bodies[1].mass * acc[1]

        self.assertLess(total_force_like.norm(), 1e-12)

    def test_center_of_mass_is_finite_for_inner_solar_system(self) -> None:
        bodies = load_scenario("inner_solar_system")
        com = center_of_mass(bodies)

        self.assertTrue(math.isfinite(com.x))
        self.assertTrue(math.isfinite(com.y))

    def test_blank_scenario_has_no_bodies(self) -> None:
        self.assertEqual(load_scenario("blank"), [])

    def test_single_sun_scenario_has_one_body(self) -> None:
        bodies = load_scenario("single_sun")

        self.assertEqual(len(bodies), 1)
        self.assertEqual(bodies[0].name, "Sun")

    def test_elliptical_sun_earth_distance_changes_over_orbit(self) -> None:
        sim = Simulation(load_scenario("sun_earth_elliptical"), dt=1.0 / 365.25)
        distances = []

        for _ in range(366):
            sim.step()
            distances.append((sim.bodies[1].position - sim.bodies[0].position).norm())

        self.assertGreater(max(distances) - min(distances), 0.025)

    def test_periapsis_speed_is_faster_than_circular_speed_at_one_au_like_ellipse(self) -> None:
        speed = periapsis_speed(1.0, 3.003e-6, 0.9833, 1.0167)

        self.assertGreater(speed, 2.0 * math.pi)

    def test_circular_speed_at_one_au_is_two_pi_in_normalized_units(self) -> None:
        self.assertAlmostEqual(circular_speed(1.0, 0.0, 1.0), 2.0 * math.pi)

    def test_escape_speed_is_sqrt_two_times_circular_speed(self) -> None:
        self.assertAlmostEqual(escape_speed(1.0, 0.0, 1.0), math.sqrt(2.0) * circular_speed(1.0, 0.0, 1.0))

    def test_orbital_period_at_one_au_is_one_year(self) -> None:
        self.assertAlmostEqual(orbital_period(1.0, 0.0, 1.0), 1.0)

    def test_comet_scenario_has_obvious_elliptical_range(self) -> None:
        sim = Simulation(load_scenario("comet_sun"), dt=1.0 / 365.25)
        distances = []

        for _ in range(900):
            sim.step()
            distances.append((sim.bodies[1].position - sim.bodies[0].position).norm())

        self.assertGreater(max(distances) - min(distances), 1.0)


if __name__ == "__main__":
    unittest.main()
