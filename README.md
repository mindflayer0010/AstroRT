# AstroRT

AstroRT is an AI-powered real-time space physics simulator in phases. This repo currently contains Phase 1 (Version 1.1): a fully validated Python research prototype for learning 2D N-body orbital dynamics.

The master project plan lives in [ASTRO_RT_MASTER_PLAN.md](ASTRO_RT_MASTER_PLAN.md).
The running development journal lives in [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md).
The Phase 1 physics walkthrough lives in [docs/phase1_physics_walkthrough.md](docs/phase1_physics_walkthrough.md).
The Phase 1.1 browser visualizer notes live in [docs/phase1_browser_visualizer.md](docs/phase1_browser_visualizer.md).
The Phase 1 wrap-up report lives in [PHASE_1_REPORT.md](PHASE_1_REPORT.md).

## Phase 1 (Version 1.1) Status

Phase 1 is officially complete and mathematically validated!

Implements:

- 2D body model
- Newtonian pairwise gravity
- Velocity-Verlet integration
- Total energy and angular momentum metrics
- Sun-Earth, binary star, and inner Solar System scenarios
- Elliptical Sun-Earth, elliptical inner Solar System, and comet scenarios
- Blank workspace, single-star workspace, Sun-Jupiter, and three-body lab scenarios
- Headless demo for quick validation
- Optional Pygame viewer
- Local browser visualizer
- Click-drag body creation in the browser visualizer
- Browser body editing, focus, zoom, fit-to-system, and edge indicators
- Save/load current systems as JSON
- Export Phase 1 telemetry/data as JSON
- Physics sanity tests
- Browser collision/merge guardrail for very close encounters

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

This first slice of Phase 1 runs on the Python standard library. The `pip install`
step is still recommended because it makes imports and tests more convenient.

For the optional visual demo:

```bash
pip install -e .[dev,viz]
```

## Run

If you have not installed the package yet, run from the source checkout by setting `PYTHONPATH`.

Browser visualizer:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.server
```

Then open:

```text
http://127.0.0.1:8000
```

Browser controls:

- Pause/play the simulation.
- Reset the current scenario.
- Switch scenarios.
- Change simulation speed, including very slow fractional stepping.
- Click `Add body`, then click-drag on the canvas to create a new body and set its starting velocity.
- After a body is added, the app leaves add mode and selects the new body so it
  can be edited immediately.
- Use `Kind` in the Add tab for guided presets: asteroid, Earth-like,
  Jupiter-like, star, or custom.
- Use `New mass` before dragging to choose how massive the new body will be.
- Enable `No initial velocity` to drop a stationary mass into the system.
- Enable `Orbit` and choose `Around` to give the new body circular orbital velocity around a selected object.
- Use `Ecc` with `Orbit`; `0` is circular, larger values create more stretched elliptical starts.
- Watch the Add tab's orbital calculator for radius, circular speed, escape
  speed, period, drag speed, and speed error.
- Use `Lock` to follow the Sun, Earth, or any user-added body.
- Use `Zoom` to see the big picture or inspect close interactions without changing physical scale.
- Click a body on the canvas or in the `Bodies` panel to lock/focus it.
- Use `Focus` to dim or isolate non-selected bodies.
- Toggle `Edge` to show/hide arrows for bodies outside the current view.
- Toggle `Velocity`, `Accel`, and `Forces` overlays to draw realtime vector
  arrows. `Forces` shows orange net-force arrows scaled by relative `m*a`.
- Use the mouse wheel to zoom around the cursor.
- Drag empty space on the canvas to pan the free camera.
- Use `Measurements` to switch distance/mass readout units and track live
  distances between multiple body pairs.
- Read the `Bodies` panel for realtime per-object physical parameters.
- Use `Selected Body` after clicking a body to edit its mass, display radius,
  and velocity components, clear its trail, or remove it from the system.
- The inspector also supports name, color, position, mass presets, freeze,
  clone, and orbit-around-selected shortcuts.
- Clicking into a selected-body edit field pauses the simulation and protects
  your typed values until you press `Apply`.
- Use `Fit system` to zoom out to the current system scale.
- Use `Reset view` to return to free camera at default zoom.
- Hover a body to see a compact live info card without opening the inspector.
- Use `Clear trails` to remove all drawn histories without changing physics.
- Open `Help` in the HUD, or press `?`, for controls and physics readout notes.
- Use `Save system` and `Load system` to preserve/reload a sandbox setup as JSON.
- Use `Export data` to download current state, metric history, units, and trails for later analysis.
- Watch the Metrics panel for stability labels and drift warnings in sensitive
  or chaotic scenarios.
- Use preset cards in the `Sim` tab for quick starter systems.
- Use timeline controls to step once, scrub/rewind from the beginning of the
  current run, restore the live simulation to a scrubbed frame, snapshot
  the current system, halve/double the real physics `dt`, or reset `dt` to the
  scenario default.
- Press `F` to fit the system, `R` to reset the view, and `.` to step once.

Portfolio/about page:

```text
http://127.0.0.1:8000/about
```
- Drag the AstroRT HUD by its header.
- Resize the HUD from its corner.
- Collapse panels or hide the whole UI with `Hide`.
- Press `H` to show/hide the UI.

Scenario note: use `blank` when you want no preset bodies, and `single_sun` when you want a clean central star for adding orbiting bodies. The original `sun_earth` and `inner_solar_system` presets are ideal circular starts for validation. Real Earth-like ellipses are subtle because Earth's eccentricity is only about `0.0167`. Use `comet_sun` or raise `Ecc` in Orbit mode when you want a visibly stretched ellipse.

Physics note: every body affects every other body. If a new body seems to have no effect, its mass is probably tiny compared with the Sun. Increase `Mass` toward `1e-2` or `1e-1` solar masses to see stronger influence.

Orbit note: `Orbit` computes a good orbital starting velocity around the selected target. `Ecc = 0` is circular; higher `Ecc` starts the body at periapsis of an elliptical orbit. The full system is still N-body, so nearby extra masses can perturb that orbit afterward.

Collision note: `Rest` means zero initial velocity, not fixed in space. Gravity still acts. The browser sim now merges bodies that pass extremely close together, conserving mass and linear momentum, so point-mass fly-throughs do not create fake numerical slingshots.

Realtime body parameters currently include mass, distance from origin, speed, acceleration magnitude, kinetic energy, and angular momentum contribution. The automatic `Closest` overlay shows the nearest pair at the current instant; custom measurement pairs are for distances you choose manually.

Headless metrics demo:

```bash
python -m astro_rt.demo --headless --scenario sun_earth --years 1
```

PowerShell from source checkout:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.demo --headless --scenario sun_earth --years 1
```

Bash from source checkout:

```bash
PYTHONPATH=src python3 -m astro_rt.demo --headless --scenario sun_earth --years 1
```

Optional Pygame viewer:

```bash
python -m astro_rt.demo --scenario sun_earth
```

PowerShell from source checkout:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.demo --scenario sun_earth
```

## Test

```bash
python -m unittest discover -s tests
```

PowerShell from source checkout:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

Bash from source checkout:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

If you installed the dev extra, this also works:

```bash
pytest -q
```

## Phase 1 Learning Notes

AstroRT uses normalized astronomy units in Phase 1:

- distance: astronomical units
- mass: solar masses
- time: Earth years

With these units, the gravitational constant becomes `G = 4 * pi^2`. That means an Earth-like body at `1 AU` with speed `2 * pi AU/year` naturally completes roughly one orbit per year around a one-solar-mass star.

The first integrator is Velocity-Verlet. It is useful for orbits because it updates positions and velocities in a way that keeps energy behavior much healthier than a naive Euler step.
