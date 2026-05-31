"""Local browser visualizer for AstroRT Phase 1.1.

This is intentionally built with Python's standard library. FastAPI comes
later, but this file lets us run a browser app right now without installing
backend dependencies.
"""

from __future__ import annotations

import argparse
import json
from math import isfinite
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from astro_rt.body import Body
from astro_rt.forces import accelerations
from astro_rt.metrics import center_of_mass, center_of_mass_velocity, closest_pair, relative_error, total_momentum
from astro_rt.orbits import periapsis_speed_from_eccentricity
from astro_rt.scenarios import SCENARIOS, load_scenario, scenario_info
from astro_rt.simulation import Simulation
from astro_rt.vector import vec2

ROOT_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT_DIR / "web"
# Browser dt is smaller than the first headless demo dt so high-eccentricity
# orbits have more samples near periapsis, where they move fastest.
DEFAULT_DT = 1.0 / (365.25 * 4.0)
# Browser-only merge guardrail. This is intentionally larger than real solar
# radii so interactive point-mass fly-throughs merge instead of numerically
# exploding near r=0.
DEFAULT_COLLISION_DISTANCE = 0.05


class BrowserSimulationApp:
    """Owns the one running simulation used by the local browser app."""

    def __init__(self, scenario: str = "single_sun", dt: float = DEFAULT_DT):
        self.base_dt = dt
        self.scenario = scenario
        self.dt = self._dt_for_scenario(scenario)
        self.sim = Simulation(
            load_scenario(scenario),
            dt=self.dt,
            softening=scenario_info(scenario).softening,
            collision_distance=DEFAULT_COLLISION_DISTANCE,
        )

    def reset(self, scenario: str | None = None) -> dict:
        """Restart the simulation, optionally switching scenario."""

        if scenario is not None:
            self.scenario = scenario
        self.dt = self._dt_for_scenario(self.scenario)
        self.sim = Simulation(
            load_scenario(self.scenario),
            dt=self.dt,
            softening=scenario_info(self.scenario).softening,
            collision_distance=DEFAULT_COLLISION_DISTANCE,
        )
        return self.state()

    def step(self, steps: int) -> dict:
        """Advance the simulation and return a JSON-ready state payload."""

        self.sim.step(max(0, steps))
        return self.state()

    def set_dt(self, payload: dict) -> dict:
        """Change the active physics timestep.

        This is different from browser playback speed. Speed decides how many
        steps happen per visual frame; `dt` decides how much simulated time one
        physics step represents. Smaller `dt` usually improves close-encounter
        accuracy at the cost of needing more steps to cover the same years.
        """

        dt = float(payload["dt"])
        if not isfinite(dt) or dt <= 0.0:
            raise ValueError("dt must be a positive finite number")
        self.dt = dt
        self.sim.dt = dt
        self.sim.reset_metric_baseline()
        return self.state()

    def reset_dt(self) -> dict:
        """Restore the scenario's recommended browser timestep."""

        self.dt = self._dt_for_scenario(self.scenario)
        self.sim.dt = self.dt
        self.sim.reset_metric_baseline()
        return self.state()

    def add_body(self, payload: dict) -> dict:
        """Create a new body from browser-supplied position and velocity."""

        body_index = len(self.sim.bodies) + 1
        color = payload.get("color", [120, 220, 255])
        mass = float(payload.get("mass", 1.0e-6))
        if not isfinite(mass) or mass <= 0.0:
            raise ValueError("mass must be a positive finite number")
        position = vec2(float(payload["x"]), float(payload["y"]))
        velocity = vec2(float(payload.get("vx", 0.0)), float(payload.get("vy", 0.0)))

        # If the browser asks for an orbit target, compute a tangential orbital
        # velocity around that body. Eccentricity 0 gives a circular orbit;
        # larger values start the body at periapsis of an elliptical orbit.
        orbit_target = payload.get("orbitTarget")
        if orbit_target:
            eccentricity = float(payload.get("orbitEccentricity", 0.0))
            velocity = self._orbit_velocity(position, mass, str(orbit_target), eccentricity)

        body = Body(
            name=str(payload.get("name", f"Body {body_index}")),
            mass=mass,
            position=position,
            velocity=velocity,
            radius=float(payload.get("radius", 4.0)),
            color=(int(color[0]), int(color[1]), int(color[2])),
        )
        self.sim.add_body(body)
        return self.state()

    def update_body(self, payload: dict) -> dict:
        """Edit physical/display parameters for an existing body.

        Phase 1 keeps editing intentionally explicit: position is left alone
        for now, while mass and velocity can be changed from the inspector.
        """

        body = self.sim.find_body(str(payload["name"]))

        if "mass" in payload:
            mass = float(payload["mass"])
            if not isfinite(mass) or mass <= 0.0:
                raise ValueError("mass must be a positive finite number")
            body.mass = mass

        if "newName" in payload:
            new_name = str(payload["newName"]).strip()
            if not new_name:
                raise ValueError("name cannot be empty")
            if new_name != body.name and any(other.name == new_name for other in self.sim.bodies):
                raise ValueError(f"body name already exists: {new_name}")
            body.name = new_name

        if "x" in payload or "y" in payload:
            x = float(payload.get("x", body.position.x))
            y = float(payload.get("y", body.position.y))
            if not isfinite(x) or not isfinite(y):
                raise ValueError("position must be finite")
            body.position = vec2(x, y)

        if "vx" in payload or "vy" in payload:
            vx = float(payload.get("vx", body.velocity.x))
            vy = float(payload.get("vy", body.velocity.y))
            if not isfinite(vx) or not isfinite(vy):
                raise ValueError("velocity must be finite")
            body.velocity = vec2(vx, vy)

        if "radius" in payload:
            radius = float(payload["radius"])
            if not isfinite(radius) or radius <= 0.0:
                raise ValueError("radius must be a positive finite number")
            body.radius = radius

        if "color" in payload:
            color = payload["color"]
            body.color = (int(color[0]), int(color[1]), int(color[2]))

        # Any edit to mass or velocity changes the active system. Resetting the
        # baseline makes drift read as "from this edited state onward".
        self.sim.reset_metric_baseline()
        return self.state()

    def clone_body(self, payload: dict) -> dict:
        """Duplicate an existing body with a tiny position offset."""

        source = self.sim.find_body(str(payload["name"]))
        clone = source.copy()
        clone.name = self._unique_body_name(f"{source.name} copy")
        clone.position = vec2(source.position.x + 0.05, source.position.y + 0.05)
        clone.trail.clear()
        self.sim.add_body(clone)
        return self.state()

    def freeze_body(self, payload: dict) -> dict:
        """Set one body's velocity to zero."""

        body = self.sim.find_body(str(payload["name"]))
        body.velocity = vec2(0.0, 0.0)
        self.sim.reset_metric_baseline()
        return self.state()

    def remove_body(self, payload: dict) -> dict:
        """Remove one body from the running sandbox."""

        self.sim.remove_body(str(payload["name"]))
        return self.state()

    def clear_body_trail(self, payload: dict) -> dict:
        """Clear display history for one body without changing its physics."""

        self.sim.find_body(str(payload["name"])).trail.clear()
        return self.state()

    def clear_all_trails(self) -> dict:
        """Clear all display trails while keeping positions and velocities."""

        self.sim.reset_trails()
        return self.state()

    def export_system(self) -> dict:
        """Return a portable JSON description of the current system.

        This is a scenario snapshot: enough to rebuild the current bodies later
        without including transient UI state.
        """

        return {
            "format": "astro_rt_system",
            "version": 1,
            "scenario": self.scenario,
            "time": self.sim.time,
            "dt": self.dt,
            "defaultDt": self._dt_for_scenario(self.scenario),
            "softening": self.sim.softening,
            "collisionDistance": self.sim.collision_distance,
            "bodies": [self._body_system_payload(body) for body in self.sim.bodies],
        }

    def load_system(self, payload: dict) -> dict:
        """Replace the running system with bodies from exported JSON."""

        if payload.get("format") not in {None, "astro_rt_system"}:
            raise ValueError("unsupported system format")

        bodies = [self._body_from_payload(body_data) for body_data in payload.get("bodies", [])]
        self.scenario = str(payload.get("scenario", "custom"))
        if self.scenario not in SCENARIOS:
            self.scenario = "custom"
        self.sim = Simulation(
            bodies,
            dt=float(payload.get("dt", self.dt)),
            softening=float(payload.get("softening", 0.0)),
            collision_distance=float(payload.get("collisionDistance", DEFAULT_COLLISION_DISTANCE)),
        )
        self.dt = self.sim.dt
        self.sim.time = float(payload.get("time", 0.0))
        self.sim.reset_metric_baseline()
        return self.state()

    def export_data(self) -> dict:
        """Return learning/analysis data from the current run.

        Phase 1 exports JSON instead of a binary dataset so the structure stays
        inspectable while we are learning.
        """

        return {
            "format": "astro_rt_phase1_data",
            "version": 1,
            "scenario": self.scenario,
            "units": {
                "distance": "AU",
                "time": "years",
                "mass": "solar masses",
                "velocity": "AU/year",
            },
            "dt": self.dt,
            "currentState": self.state(),
            "metricHistory": [
                {
                    "time": snapshot.time,
                    "energy": snapshot.energy,
                    "angularMomentumZ": snapshot.angular_momentum_z,
                }
                for snapshot in self.sim.metric_history
            ],
            "bodyTrails": {body.name: body.trail for body in self.sim.bodies},
        }

    def _body_system_payload(self, body: Body) -> dict:
        """Serialize one body for save/load."""

        return {
            "name": body.name,
            "mass": body.mass,
            "position": body.position.as_tuple(),
            "velocity": body.velocity.as_tuple(),
            "radius": body.radius,
            "color": body.color,
        }

    def _body_from_payload(self, payload: dict) -> Body:
        """Create a Body from trusted exported fields with basic validation."""

        mass = float(payload["mass"])
        if not isfinite(mass) or mass <= 0.0:
            raise ValueError("body mass must be a positive finite number")
        position = payload["position"]
        velocity = payload["velocity"]
        color = payload.get("color", [255, 255, 255])
        return Body(
            name=str(payload["name"]),
            mass=mass,
            position=vec2(float(position[0]), float(position[1])),
            velocity=vec2(float(velocity[0]), float(velocity[1])),
            radius=max(1.0, float(payload.get("radius", 4.0))),
            color=(int(color[0]), int(color[1]), int(color[2])),
        )

    def _orbit_velocity(self, position, mass: float, target_name: str, eccentricity: float):
        """Return prograde periapsis velocity around a named target body."""

        target = next((body for body in self.sim.bodies if body.name == target_name), None)
        if target is None:
            raise ValueError(f"Unknown orbit target: {target_name}")

        radial = position - target.position
        distance = radial.norm()
        if distance == 0.0:
            raise ValueError("Cannot orbit from the exact center of the target")

        tangent = vec2(-radial.y / distance, radial.x / distance)
        bounded_eccentricity = max(0.0, min(0.95, eccentricity))
        speed = periapsis_speed_from_eccentricity(
            target.mass,
            mass,
            distance,
            bounded_eccentricity,
        )
        return target.velocity + tangent * speed

    def _dt_for_scenario(self, scenario: str) -> float:
        """Return the browser timestep after applying scenario-specific hints."""

        return self.base_dt * scenario_info(scenario).dt_scale

    def _unique_body_name(self, base: str) -> str:
        """Return a body name that does not collide with current names."""

        names = {body.name for body in self.sim.bodies}
        if base not in names:
            return base
        index = 2
        while f"{base} {index}" in names:
            index += 1
        return f"{base} {index}"

    def state(self) -> dict:
        """Convert the current simulation into plain JSON-safe data."""

        snapshot = self.sim.snapshot()
        current_accelerations = accelerations(self.sim.bodies, self.sim.softening)
        com = center_of_mass(self.sim.bodies)
        com_velocity = center_of_mass_velocity(self.sim.bodies)
        momentum = total_momentum(self.sim.bodies)
        closest_a, closest_b, closest_distance = closest_pair(self.sim.bodies)
        max_acceleration = max((acc.norm() for acc in current_accelerations), default=0.0)
        energy_drift = relative_error(snapshot.energy, self.sim.initial_energy)
        angular_momentum_drift = relative_error(
            snapshot.angular_momentum_z,
            self.sim.initial_angular_momentum_z,
        )
        info = scenario_info(self.scenario)
        return {
            "scenario": self.scenario,
            "scenarioInfo": {
                "label": info.label,
                "stability": info.stability,
                "note": info.note,
                "dtScale": info.dt_scale,
                "softening": self.sim.softening,
            },
            "time": self.sim.time,
            "dt": self.dt,
            "defaultDt": self._dt_for_scenario(self.scenario),
            "softening": self.sim.softening,
            "collisionDistance": self.sim.collision_distance,
            "energy": snapshot.energy,
            "angularMomentumZ": snapshot.angular_momentum_z,
            "energyDrift": energy_drift,
            "angularMomentumDrift": angular_momentum_drift,
            "warnings": self._warnings(energy_drift, angular_momentum_drift),
            "diagnostics": {
                "centerOfMass": com.as_tuple(),
                "centerOfMassVelocity": com_velocity.as_tuple(),
                "totalMomentum": momentum.as_tuple(),
                "closestPair": {
                    "a": closest_a,
                    "b": closest_b,
                    "distance": closest_distance,
                },
                "maxAcceleration": max_acceleration,
            },
            "scenarios": sorted(SCENARIOS),
            "bodies": [self._body_payload(body, current_accelerations[index]) for index, body in enumerate(self.sim.bodies)],
        }

    def _warnings(self, energy_drift: float, angular_momentum_drift: float) -> list[str]:
        """Return user-facing numerical-health warnings for the current state."""

        warnings = []
        info = scenario_info(self.scenario)
        if info.stability == "chaotic":
            warnings.append(info.note)
        elif info.stability == "sensitive":
            warnings.append(info.note)

        if energy_drift > 1.0e-2:
            warnings.append("High energy drift: reduce speed, use a smaller timestep, or avoid close encounters.")
        elif energy_drift > 1.0e-4:
            warnings.append("Moderate energy drift: this scenario is numerically sensitive.")

        if angular_momentum_drift > 1.0e-6:
            warnings.append("Angular momentum drift is rising; inspect close encounters or timestep size.")

        return warnings

    def _body_payload(self, body: Body, acceleration) -> dict:
        """Return realtime physical parameters for one body.

        These values are computed on the Python side so the browser displays
        the same physics state that drives the simulation.
        """

        speed = body.velocity.norm()
        acceleration_magnitude = acceleration.norm()
        kinetic_energy = 0.5 * body.mass * speed * speed
        angular_momentum_z = body.mass * (
            body.position.x * body.velocity.y - body.position.y * body.velocity.x
        )
        return {
            "name": body.name,
            "mass": body.mass,
            "position": body.position.as_tuple(),
            "velocity": body.velocity.as_tuple(),
            "speed": speed,
            "acceleration": acceleration.as_tuple(),
            "accelerationMagnitude": acceleration_magnitude,
            "kineticEnergy": kinetic_energy,
            "distanceFromOrigin": body.position.norm(),
            "angularMomentumZ": angular_momentum_z,
            "radius": body.radius,
            "color": body.color,
            # Keep the wire payload bounded. The server stores a longer trail,
            # but the browser only needs recent points to draw.
            "trail": body.trail[-700:],
        }


def make_handler(app: BrowserSimulationApp) -> type[BaseHTTPRequestHandler]:
    """Create a request handler class bound to one simulation app instance."""

    class AstroRTRequestHandler(BaseHTTPRequestHandler):
        # Silence the default noisy request logging; our CLI message is enough
        # for this tiny local server.
        def log_message(self, format: str, *args) -> None:  # noqa: A002
            return

        def do_GET(self) -> None:
            parsed = urlparse(self.path)

            if parsed.path in {"/", "/index.html"}:
                self._send_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
                return

            if parsed.path in {"/about", "/about.html"}:
                self._send_file(WEB_DIR / "about.html", "text/html; charset=utf-8")
                return

            if parsed.path == "/app.js":
                self._send_file(WEB_DIR / "app.js", "application/javascript; charset=utf-8")
                return

            if parsed.path == "/styles.css":
                self._send_file(WEB_DIR / "styles.css", "text/css; charset=utf-8")
                return

            if parsed.path == "/api/state":
                params = parse_qs(parsed.query)
                steps = int(params.get("steps", ["1"])[0])
                self._send_json(app.step(steps))
                return

            if parsed.path == "/api/reset":
                params = parse_qs(parsed.query)
                scenario = params.get("scenario", [None])[0]
                if scenario is not None and scenario not in SCENARIOS:
                    self._send_json({"error": f"Unknown scenario: {scenario}"}, HTTPStatus.BAD_REQUEST)
                    return
                self._send_json(app.reset(scenario))
                return

            if parsed.path == "/api/export_system":
                self._send_json(app.export_system())
                return

            if parsed.path == "/api/export_data":
                self._send_json(app.export_data())
                return

            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)

            if parsed.path == "/api/add_body":
                try:
                    payload = self._read_json()
                    self._send_json(app.add_body(payload), HTTPStatus.CREATED)
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid body payload: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/update_body":
                try:
                    payload = self._read_json()
                    self._send_json(app.update_body(payload))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid body update: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/remove_body":
                try:
                    payload = self._read_json()
                    self._send_json(app.remove_body(payload))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid body removal: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/clone_body":
                try:
                    payload = self._read_json()
                    self._send_json(app.clone_body(payload), HTTPStatus.CREATED)
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid body clone: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/freeze_body":
                try:
                    payload = self._read_json()
                    self._send_json(app.freeze_body(payload))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid body freeze: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/clear_body_trail":
                try:
                    payload = self._read_json()
                    self._send_json(app.clear_body_trail(payload))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid trail clear: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/clear_all_trails":
                self._send_json(app.clear_all_trails())
                return

            if parsed.path == "/api/set_dt":
                try:
                    payload = self._read_json()
                    self._send_json(app.set_dt(payload))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid timestep update: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/reset_dt":
                self._send_json(app.reset_dt())
                return

            if parsed.path == "/api/load_system":
                try:
                    payload = self._read_json()
                    self._send_json(app.load_system(payload))
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    self._send_json({"error": f"Invalid system payload: {exc}"}, HTTPStatus.BAD_REQUEST)
                return

            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

        def _send_file(self, path: Path, content_type: str) -> None:
            if not path.exists():
                self._send_json({"error": f"Missing file: {path.name}"}, HTTPStatus.NOT_FOUND)
                return

            data = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            return json.loads(raw.decode("utf-8"))

    return AstroRTRequestHandler


def run_server(host: str, port: int, scenario: str) -> None:
    """Start the local development server."""

    app = BrowserSimulationApp(scenario=scenario)
    server = ThreadingHTTPServer((host, port), make_handler(app))
    print(f"AstroRT browser visualizer running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AstroRT Phase 1.1 browser visualizer.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="single_sun")
    args = parser.parse_args()

    run_server(args.host, args.port, args.scenario)


if __name__ == "__main__":
    main()
