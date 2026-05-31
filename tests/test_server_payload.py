from __future__ import annotations

from math import sqrt
import unittest

from astro_rt.constants import G
from astro_rt.forces import accelerations
from astro_rt.server import BrowserSimulationApp


class BrowserSimulationAppTests(unittest.TestCase):
    def test_state_payload_contains_browser_visualizer_fields(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        state = app.state()

        self.assertEqual(state["scenario"], "sun_earth")
        self.assertIn("energyDrift", state)
        self.assertIn("angularMomentumDrift", state)
        self.assertIn("scenarioInfo", state)
        self.assertIn("warnings", state)
        self.assertIn("softening", state)
        self.assertIn("collisionDistance", state)
        self.assertIn("defaultDt", state)
        self.assertIn("diagnostics", state)
        self.assertIn("sun_earth", state["scenarios"])
        self.assertGreaterEqual(len(state["bodies"]), 2)
        self.assertIn("position", state["bodies"][0])
        self.assertIn("trail", state["bodies"][0])
        self.assertIn("speed", state["bodies"][0])
        self.assertIn("acceleration", state["bodies"][0])
        self.assertIn("accelerationMagnitude", state["bodies"][0])
        self.assertIn("kineticEnergy", state["bodies"][0])
        self.assertIn("distanceFromOrigin", state["bodies"][0])
        self.assertIn("angularMomentumZ", state["bodies"][0])
        self.assertIn("centerOfMass", state["diagnostics"])
        self.assertIn("closestPair", state["diagnostics"])

    def test_step_advances_time(self) -> None:
        app = BrowserSimulationApp()
        before = app.state()["time"]

        after = app.step(3)["time"]

        self.assertGreater(after, before)

    def test_reset_can_switch_scenarios(self) -> None:
        app = BrowserSimulationApp()

        state = app.reset("binary_stars")

        self.assertEqual(state["scenario"], "binary_stars")
        self.assertEqual(len(state["bodies"]), 2)

    def test_sensitive_scenarios_use_numerical_guardrails(self) -> None:
        app = BrowserSimulationApp("three_body_lab")
        state = app.state()

        self.assertEqual(state["scenarioInfo"]["stability"], "chaotic")
        self.assertGreater(state["softening"], 0.0)
        self.assertLess(state["dt"], app.base_dt)
        self.assertTrue(state["warnings"])

    def test_drift_warning_appears_when_energy_error_is_high(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        app.sim.initial_energy = app.sim.initial_energy * 0.5

        state = app.state()

        self.assertTrue(any("energy drift" in warning.lower() for warning in state["warnings"]))

    def test_blank_workspace_can_start_empty_and_accept_stationary_body(self) -> None:
        app = BrowserSimulationApp("blank")
        self.assertEqual(app.state()["bodies"], [])

        state = app.add_body({"x": 0.0, "y": 0.0, "mass": 1.0})

        self.assertEqual(len(state["bodies"]), 1)
        self.assertEqual(state["bodies"][0]["velocity"], (0.0, 0.0))

    def test_add_body_appends_body_and_resets_metric_baseline(self) -> None:
        app = BrowserSimulationApp()
        before_count = len(app.state()["bodies"])

        state = app.add_body(
            {
                "x": 1.2,
                "y": 0.0,
                "vx": 0.0,
                "vy": 5.5,
                "mass": 1.0e-6,
                "radius": 4,
                "color": [120, 230, 180],
            }
        )

        self.assertEqual(len(state["bodies"]), before_count + 1)
        self.assertEqual(state["bodies"][-1]["name"], f"Body {before_count + 1}")
        self.assertAlmostEqual(state["bodies"][-1]["mass"], 1.0e-6)
        self.assertEqual(state["energyDrift"], 0.0)

    def test_add_body_can_default_to_no_initial_velocity(self) -> None:
        app = BrowserSimulationApp()

        state = app.add_body({"x": 1.4, "y": -0.2})

        self.assertEqual(state["bodies"][-1]["velocity"], (0.0, 0.0))

    def test_added_body_changes_existing_body_acceleration(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        before = accelerations(app.sim.bodies)[1]

        app.add_body({"x": 1.2, "y": 0.0, "mass": 0.1})
        after = accelerations(app.sim.bodies)[1]

        self.assertGreater((after - before).norm(), 1.0)

    def test_add_body_can_compute_circular_orbit_velocity_around_target(self) -> None:
        app = BrowserSimulationApp()

        state = app.add_body({"x": 1.5, "y": 0.0, "mass": 1.0e-6, "orbitTarget": "Sun"})
        added = state["bodies"][-1]

        sun_velocity_y = app.sim.bodies[0].velocity.y
        expected_speed = sun_velocity_y + sqrt(G * (1.0 + 1.0e-6) / 1.5)
        self.assertAlmostEqual(added["velocity"][0], 0.0, places=12)
        self.assertAlmostEqual(added["velocity"][1], expected_speed, places=12)

    def test_orbit_eccentricity_increases_periapsis_speed(self) -> None:
        app = BrowserSimulationApp()

        circular = app.add_body({"x": 2.0, "y": 0.0, "mass": 1.0e-8, "orbitTarget": "Sun"})
        circular_speed = circular["bodies"][-1]["speed"]
        app.reset("sun_earth")
        eccentric = app.add_body(
            {
                "x": 2.0,
                "y": 0.0,
                "mass": 1.0e-8,
                "orbitTarget": "Sun",
                "orbitEccentricity": 0.8,
            }
        )
        eccentric_speed = eccentric["bodies"][-1]["speed"]

        self.assertGreater(eccentric_speed, circular_speed)

    def test_update_body_changes_mass_velocity_radius_and_resets_baseline(self) -> None:
        app = BrowserSimulationApp("single_sun")

        state = app.update_body(
            {
                "name": "Sun",
                "newName": "Primary",
                "mass": 0.8,
                "x": 0.1,
                "y": -0.2,
                "vx": 0.25,
                "vy": -0.5,
                "radius": 12,
            }
        )
        sun = state["bodies"][0]

        self.assertEqual(sun["name"], "Primary")
        self.assertAlmostEqual(sun["mass"], 0.8)
        self.assertEqual(sun["position"], (0.1, -0.2))
        self.assertEqual(sun["velocity"], (0.25, -0.5))
        self.assertEqual(sun["radius"], 12)
        self.assertEqual(state["energyDrift"], 0.0)

    def test_clone_and_freeze_body_actions(self) -> None:
        app = BrowserSimulationApp("single_sun")

        cloned = app.clone_body({"name": "Sun"})
        self.assertEqual(len(cloned["bodies"]), 2)
        self.assertEqual(cloned["bodies"][1]["name"], "Sun copy")

        frozen = app.freeze_body({"name": "Sun copy"})
        copy = next(body for body in frozen["bodies"] if body["name"] == "Sun copy")
        self.assertEqual(copy["velocity"], (0.0, 0.0))

    def test_set_dt_changes_physics_timestep(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        before = app.state()["dt"]

        state = app.set_dt({"dt": before * 0.5})

        self.assertAlmostEqual(state["dt"], before * 0.5)
        self.assertAlmostEqual(app.sim.dt, before * 0.5)
        self.assertEqual(state["energyDrift"], 0.0)

    def test_reset_dt_restores_scenario_default_timestep(self) -> None:
        app = BrowserSimulationApp("comet_sun")
        default_dt = app.state()["defaultDt"]
        app.set_dt({"dt": default_dt * 0.25})

        state = app.reset_dt()

        self.assertAlmostEqual(state["dt"], default_dt)
        self.assertAlmostEqual(app.sim.dt, default_dt)
        self.assertEqual(state["energyDrift"], 0.0)

    def test_remove_body_deletes_body_and_resets_baseline(self) -> None:
        app = BrowserSimulationApp("sun_earth")

        state = app.remove_body({"name": "Earth"})

        self.assertEqual([body["name"] for body in state["bodies"]], ["Sun"])
        self.assertEqual(state["energyDrift"], 0.0)

    def test_clear_body_trail_only_removes_display_history(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        app.step(4)
        self.assertGreater(len(app.sim.find_body("Earth").trail), 0)

        state = app.clear_body_trail({"name": "Earth"})

        earth = next(body for body in state["bodies"] if body["name"] == "Earth")
        self.assertEqual(earth["trail"], [])
        self.assertGreater(len(app.sim.find_body("Sun").trail), 0)

    def test_clear_all_trails_removes_display_history_for_every_body(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        app.step(4)

        state = app.clear_all_trails()

        self.assertTrue(all(body["trail"] == [] for body in state["bodies"]))

    def test_export_and_load_system_round_trip(self) -> None:
        app = BrowserSimulationApp("blank")
        app.add_body({"x": 0.0, "y": 0.0, "mass": 1.0, "name": "Primary"})
        app.add_body({"x": 1.0, "y": 0.0, "mass": 1.0e-6, "vy": 6.0, "name": "Probe"})
        exported = app.export_system()

        loaded = BrowserSimulationApp("single_sun")
        state = loaded.load_system(exported)

        self.assertEqual([body["name"] for body in state["bodies"]], ["Primary", "Probe"])
        self.assertAlmostEqual(state["bodies"][1]["velocity"][1], 6.0)
        self.assertEqual(state["energyDrift"], 0.0)

    def test_load_system_can_restore_a_state_snapshot(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        snapshot = app.step(4)
        payload = {
            "format": "astro_rt_system",
            "scenario": snapshot["scenario"],
            "time": snapshot["time"],
            "dt": snapshot["dt"],
            "softening": snapshot["softening"],
            "collisionDistance": snapshot["collisionDistance"],
            "bodies": [
                {
                    "name": body["name"],
                    "mass": body["mass"],
                    "position": body["position"],
                    "velocity": body["velocity"],
                    "radius": body["radius"],
                    "color": body["color"],
                }
                for body in snapshot["bodies"]
            ],
        }

        restored = BrowserSimulationApp("blank").load_system(payload)

        self.assertEqual(restored["scenario"], "sun_earth")
        self.assertAlmostEqual(restored["time"], snapshot["time"])
        self.assertEqual([body["name"] for body in restored["bodies"]], ["Sun", "Earth"])
        self.assertEqual(restored["energyDrift"], 0.0)

    def test_browser_collision_guard_merges_close_bodies(self) -> None:
        app = BrowserSimulationApp("single_sun")
        state = app.add_body({"x": 0.01, "y": 0.0, "mass": 0.1, "name": "Incoming"})
        self.assertEqual(len(state["bodies"]), 2)

        merged = app.step(1)

        self.assertEqual(len(merged["bodies"]), 1)
        self.assertEqual(merged["bodies"][0]["name"], "Sun")
        self.assertAlmostEqual(merged["bodies"][0]["mass"], 1.1)

    def test_export_data_contains_units_metrics_and_trails(self) -> None:
        app = BrowserSimulationApp("sun_earth")
        app.step(3)

        exported = app.export_data()

        self.assertEqual(exported["format"], "astro_rt_phase1_data")
        self.assertEqual(exported["units"]["distance"], "AU")
        self.assertGreaterEqual(len(exported["metricHistory"]), 4)
        self.assertIn("Earth", exported["bodyTrails"])

    def test_update_body_rejects_invalid_mass(self) -> None:
        app = BrowserSimulationApp("single_sun")

        with self.assertRaises(ValueError):
            app.update_body({"name": "Sun", "mass": -1.0})


if __name__ == "__main__":
    unittest.main()
