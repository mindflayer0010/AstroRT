# AstroRT Development Log

This file records every meaningful change we make while building AstroRT. The master plan explains where the project is going; this log explains what changed, why it changed, how it works, and how we verified it.

## 2026-05-28 - Project Planning Foundation

### What Changed

- Added `ASTRO_RT_MASTER_PLAN.md`.
- Defined AstroRT as a phased AI-powered real-time space physics simulator.
- Locked the long-term architecture:
  - Phase 1: Python physics prototype.
  - Phase 2: C++ physics engine.
  - Phase 3: pybind11 bindings.
  - Phase 4: PyTorch AI/ML layer.
  - Phase 5: React/Next.js + Three.js web platform.
  - Phase 6: deployment, benchmarks, reports, and portfolio polish.

### Why

AstroRT is a large project, so it needs one planning source before implementation. The master plan prevents us from jumping into random code and losing the bigger architecture.

### How

The plan was organized into 23 sections covering vision, problem, solution, features, architecture, stack, phase roadmap, testing, datasets, sources, decision log, and open questions.

### Verification

- Confirmed all 23 requested sections exist.
- Confirmed no implementation files were created during the planning step.
- Confirmed the decision log includes the major architecture choices.

## 2026-05-28 - Phase 1 Python Prototype Started

### What Changed

Added the first runnable Phase 1 Python prototype:

- `pyproject.toml`
- `README.md`
- `.gitignore`
- `src/astro_rt/__init__.py`
- `src/astro_rt/constants.py`
- `src/astro_rt/vector.py`
- `src/astro_rt/body.py`
- `src/astro_rt/forces.py`
- `src/astro_rt/integrators.py`
- `src/astro_rt/metrics.py`
- `src/astro_rt/simulation.py`
- `src/astro_rt/scenarios.py`
- `src/astro_rt/demo.py`
- `tests/test_phase1_physics.py`

### Why

Phase 1 needs a small but real physics core before any AI, C++, or web work. The purpose is to learn and validate:

- How gravity becomes code.
- Why integrators matter.
- How to measure physical correctness.
- How to keep code simple enough to later port into C++.

### How

The first implementation uses a direct 2D N-body approach:

- Each body has mass, position, and velocity.
- Gravity is calculated by summing acceleration from every other body.
- The simulation advances with Velocity-Verlet integration.
- Energy and angular momentum are tracked to measure physical drift.
- Scenarios provide repeatable starting systems.
- Tests check basic conservation and sanity behavior.

## 2026-05-28 - Pure Python `Vec2` Added

### What Changed

Added `src/astro_rt/vector.py` with a small `Vec2` type.

### Why

The current environment has Python but does not have `pip`, `ensurepip`, or NumPy available. A pure-Python vector type lets Phase 1 run immediately without dependency setup.

This also supports the future C++ rewrite because a small `Vec2` class maps naturally to a C++ `Vec2` struct/class.

### How

`Vec2` supports:

- Addition.
- Subtraction.
- Scalar multiplication.
- Scalar division.
- Dot product.
- Norm/magnitude.
- Tuple conversion.
- Copying.

### Verification

The physics tests and headless demos run using only the Python standard library.

## 2026-05-28 - Body Model Added

### What Changed

Added `src/astro_rt/body.py`.

### Why

A body is the basic object in the simulation: a star, planet, moon, asteroid, or future spacecraft.

### How

The `Body` dataclass stores:

- `name`
- `mass`
- `position`
- `velocity`
- `radius`
- `color`
- `trail`

The `copy()` method creates independent body instances so scenarios can be reused safely.

### Verification

Tests create simulations from scenarios and confirm that stepping one simulation does not mutate the original scenario definitions.

## 2026-05-28 - Gravity Force Calculation Added

### What Changed

Added `src/astro_rt/forces.py`.

### Why

N-body gravity is the core of AstroRT. Without this, bodies would be animated objects rather than physically interacting objects.

### How

The `accelerations()` function uses direct pairwise Newtonian gravity:

```text
acceleration_on_i = G * mass_j * direction / distance^2
```

In vector form, this becomes:

```text
a_i += G * m_j * (r_j - r_i) / |r_j - r_i|^3
```

The implementation loops over each pair once and applies equal/opposite mass-weighted acceleration effects.

### Verification

The test `test_pairwise_acceleration_respects_newtons_third_law_in_mass_weighted_form` checks that the mass-weighted acceleration sum is near zero.

## 2026-05-28 - Velocity-Verlet Integrator Added

### What Changed

Added `src/astro_rt/integrators.py`.

### Why

We need a numerical integrator to move the simulation forward in time. Velocity-Verlet is a strong first choice for orbital systems because it has much better long-term energy behavior than simple Euler integration.

### How

One Velocity-Verlet step does this:

1. Compute acceleration at the current positions.
2. Update positions using current velocity and half of the acceleration effect.
3. Compute acceleration again at the new positions.
4. Update velocities using the average of old and new acceleration.

This helps preserve orbital structure over long runs.

### Verification

The Sun-Earth scenario keeps extremely small energy drift after about one simulated year.

## 2026-05-28 - Physical Metrics Added

### What Changed

Added `src/astro_rt/metrics.py`.

### Why

A simulator can look visually correct while being physically wrong. Energy and angular momentum tracking help us detect numerical problems.

### How

The metrics module calculates:

- Kinetic energy.
- Gravitational potential energy.
- Total energy.
- Angular momentum around the z-axis.
- Center of mass.
- Relative error.

### Verification

Tests check energy and angular momentum drift in the Sun-Earth scenario.

## 2026-05-28 - Scenarios Added

### What Changed

Added `src/astro_rt/scenarios.py`.

### Why

Scenarios make the simulator repeatable. Instead of manually creating bodies each time, we can load known systems and compare behavior across code changes.

### How

Current scenarios:

- `sun_earth`
- `binary_stars`
- `inner_solar_system`

Phase 1 uses normalized astronomy units:

- distance: astronomical units
- mass: solar masses
- time: Earth years

With these units:

```text
G = 4 * pi^2
```

That means Earth at 1 AU with velocity `2 * pi AU/year` naturally orbits in about one year.

### Verification

The headless demo was run against `sun_earth` and `binary_stars`.

## 2026-05-28 - Simulation Wrapper Added

### What Changed

Added `src/astro_rt/simulation.py`.

### Why

The simulation wrapper keeps bodies, time step, current time, softening, initial metrics, stepping behavior, and trails in one place.

### How

`Simulation` supports:

- Creating a simulation from bodies.
- Stepping one or more time steps.
- Taking metric snapshots.
- Recording trails.
- Resetting trails.

### Verification

Tests step a simulation for about one year and compare final metrics against initial metrics.

## 2026-05-28 - Demo Runner Added

### What Changed

Added `src/astro_rt/demo.py`.

### Why

We need a quick way to run and observe the prototype.

### How

The demo supports:

- Headless metrics mode.
- Optional Pygame viewer.
- Scenario selection.
- Time span selection for headless runs.
- Time step selection.

Headless example:

```bash
PYTHONPATH=src python3 -m astro_rt.demo --headless --scenario sun_earth --years 1
```

### Verification

Sun-Earth one-year output:

```text
Relative energy drift: 1.116866038484e-13
Relative Lz drift: 1.256964853307e-15
```

Binary-stars quarter-year output:

```text
Relative energy drift: 1.088628129906e-08
Relative Lz drift: 2.827159716856e-16
```

## 2026-05-28 - Tests Added

### What Changed

Added `tests/test_phase1_physics.py`.

### Why

Physics tests protect us from breaking the simulator as we add interactivity, datasets, C++, and AI later.

### How

Current tests check:

- Sun-Earth energy drift.
- Sun-Earth angular momentum drift.
- Earth returns near its starting position after about one year.
- Pairwise gravity respects Newton's third law in mass-weighted form.
- Inner Solar System center of mass is finite.

### Verification

Command:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Result:

```text
Ran 4 tests
OK
```

## Ongoing Documentation Rule

From this point forward, every meaningful change should add an entry to this file with:

- What changed.
- Why it changed.
- How it works.
- How it was verified.
- Any learning note worth remembering.

## 2026-05-28 - Windows PowerShell Test Commands Documented

### What Changed

Added PowerShell and Bash source-checkout command examples to `README.md`.

### Why

The command below is Bash syntax:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

PowerShell treats `PYTHONPATH=src` as the name of a command, which causes this error:

```text
The term 'PYTHONPATH=src' is not recognized as the name of a cmdlet...
```

### How

PowerShell sets environment variables with `$env:` and separates commands with `;`:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

Latest Python test result:

```text
Ran 34 tests
OK
```

Latest Python test result:

```text
Ran 31 tests
OK
```

## 2026-05-31 - Usability Upgrade: Hover Cards, Guided Add, Timeline Restore

### What Changed

Added three usability improvements:

- Hover cards on bodies with mass, distance, speed, and acceleration.
- Guided Add Body presets: custom, asteroid, Earth-like, Jupiter-like, and star.
- `Restore here` timeline action to make a scrubbed frame become the live
  Python simulation state.

### Why

The simulator had powerful controls, but too much required opening panels or
guessing numeric values. Hover cards make inspection faster, presets make body
creation less guessy, and timeline restore turns replay into an actual editing
tool.

### How

Hover cards are browser-only UI built from the latest state payload.

Body presets set the existing mass slider plus display radius and color before
the normal `POST /api/add_body` path runs.

Timeline restore converts the currently displayed frame into the same portable
system JSON shape used by save/load, then posts it through `POST /api/load_system`.

### Verification

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## 2026-05-31 - In-App Help Tab Added

### What Changed

Added a `Help` HUD tab with:

- quick-start workflow
- mouse controls
- keyboard shortcuts
- `dt`, energy drift, vectors, and center-of-mass explanations

Also added `?` as a keyboard shortcut to open Help.

### Why

AstroRT has enough controls now that the app should explain itself in-context.
This reduces the need to jump between the simulator and markdown docs while
testing or learning.

### Verification

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## 2026-05-31 - Orbital Velocity Calculator Added

### What Changed

Added `src/astro_rt/orbits.py` with tested two-body orbital formulas:

- circular speed
- escape speed
- vis-viva elliptical speed
- periapsis speed from eccentricity
- orbital period

Added a live calculator to the Add tab showing:

- radius from the chosen target
- circular speed
- escape speed
- approximate period
- current drag speed
- speed error

### Why

Users should not have to guess the sideways velocity needed for an orbit. The
calculator makes the required orbital velocity visible while adding bodies.

### How

The backend and scenarios now share the same formulas from `orbits.py`.
The browser mirrors the same equations for immediate UI feedback while the
server remains authoritative when a body is actually added.

### Verification

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

Latest Python test result:

```text
Ran 30 tests
OK
```

## 2026-05-28 - Phase 1 Physics Walkthrough Added

### What Changed

Added `docs/phase1_physics_walkthrough.md` and linked it from `README.md`.

### Why

AstroRT is not just a build project; it is also a learning project. The walkthrough explains the current Phase 1 files in beginner-friendly but technically accurate language.

### How

The walkthrough covers:

- the full Phase 1 flow
- normalized astronomy units
- `Vec2`
- `Body`
- pairwise gravity
- Velocity-Verlet
- energy and angular momentum metrics
- scenarios
- simulation wrapper
- demo runner
- tests and what their results mean

### Verification

Documentation-only change. The walkthrough is now available at:

```text
docs/phase1_physics_walkthrough.md
```

## 2026-05-28 - Teaching Comments Added To Phase 1 Code

### What Changed

Added explanatory comments and docstrings across the Phase 1 Python code:

- `src/astro_rt/__init__.py`
- `src/astro_rt/constants.py`
- `src/astro_rt/vector.py`
- `src/astro_rt/body.py`
- `src/astro_rt/forces.py`
- `src/astro_rt/integrators.py`
- `src/astro_rt/metrics.py`
- `src/astro_rt/simulation.py`
- `src/astro_rt/scenarios.py`
- `src/astro_rt/demo.py`

### Why

AstroRT is being built as a learning project as well as a software project. The code should explain the purpose of important pieces directly where they appear.

### How

Comments were added for:

- what each module is responsible for
- what key fields such as `mass`, `position`, `velocity`, and `dt` mean
- why normalized units are used
- how pairwise gravity is calculated
- why Velocity-Verlet samples acceleration twice
- why energy and angular momentum are validation metrics
- what scenarios represent
- what the demo controls and HUD are doing
- TODO notes for known future improvements

### Verification

The change is documentation-only inside Python files, but tests should still be run after comment/docstring edits because syntax can still be broken accidentally.

## 2026-05-28 - Phase 1.1 Browser Visualizer Added

### What Changed

Added a local browser visualizer:

- `src/astro_rt/server.py`
- `web/index.html`
- `web/styles.css`
- `web/app.js`
- `docs/phase1_browser_visualizer.md`
- `tests/test_server_payload.py`

Updated `README.md` and `ASTRO_RT_MASTER_PLAN.md` with the browser visualizer command/decision.

### Why

The project needed to move from terminal-only physics output toward an app-like experience. A browser visualizer is also the first step toward the future hosted React/Three.js product.

### How

The implementation uses Python's standard library HTTP server:

- `/` serves the browser page.
- `/app.js` serves the frontend logic.
- `/styles.css` serves the visual styling.
- `/api/state?steps=N` advances the simulation and returns JSON.
- `/api/reset?scenario=name` restarts the simulation and optionally switches scenarios.

The frontend uses HTML canvas to draw:

- bodies
- trails
- labels
- time
- energy drift
- angular momentum drift

Controls include:

- pause/play
- reset
- scenario switching
- speed slider

Added inline teaching comments in the server/frontend code explaining what each layer owns and why the browser requests state from Python instead of running physics itself.

### Verification

Added tests for the browser simulation payload:

- state includes the fields the browser needs
- stepping advances time
- reset can switch scenarios

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

Latest Python test result:

```text
Ran 30 tests
OK
```

Run the visualizer:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.server
```

Then open:

```text
http://127.0.0.1:8000
```

## 2026-05-28 - Click-Drag Body Creation Added

### What Changed

Added the first sandbox-editing interaction:

- `Simulation.add_body(...)`
- `BrowserSimulationApp.add_body(...)`
- `POST /api/add_body`
- `Add body` control in the browser
- click-drag creation on the canvas
- body count display in the HUD
- browser visualizer docs updated
- test coverage for adding a body

### Why

The visualizer could previously run preset systems, but users could not change the simulation. Click-drag body creation turns the prototype into a true sandbox: you can add a new body and immediately see gravity affect it.

### How

The interaction works like this:

1. User clicks `Add body`.
2. User presses on the canvas.
3. Drag start becomes the body's position in AU.
4. Drag direction/length becomes the body's initial velocity.
5. Browser sends JSON to `POST /api/add_body`.
6. Python creates a `Body` and appends it to the running `Simulation`.
7. Energy and angular momentum baselines reset to the edited system.

The physics still runs only in Python. The browser only sends the new body's initial state and draws the returned simulation state.

### Verification

Tests:

```text
Ran 8 tests
OK
```

HTTP smoke test:

```text
POST /api/add_body -> 201
body count: 3
new body: Body 3
```

## 2026-05-29 - New Body Mass Control And Velocity Preview Added

### What Changed

Improved the browser sandbox body-creation flow:

- Added a `New mass` logarithmic slider.
- Sent the selected mass to `POST /api/add_body`.
- Scaled the new body's display radius from the selected mass.
- Added an arrowhead to the drag preview.
- Added a velocity/mass label while dragging.
- Updated docs and tests.

### Why

The previous body creation feature always used the same mass and only showed a plain line. Mass is one of the most important physical properties in AstroRT, so the user needs to feel its effect early.

### How

The mass slider stores a base-10 exponent:

```text
-6 -> 10^-6 solar masses
```

The browser converts that into a real mass value before sending it to Python.

The drag preview calculates approximate launch speed from drag length:

```text
speed = drag_length_in_AU * velocity_scale
```

### Verification

The server payload test now confirms that custom body mass is included after adding a body.

Latest test result:

```text
Ran 8 tests
OK
```

Manual API check:

```text
added bodies: 3
custom mass: 1e-05
energy drift after baseline reset: 0.0
```

## 2026-05-29 - Sandbox Control Range And Camera Lock Added

### What Changed

Improved the browser simulator controls:

- Added `No initial velocity` for stationary body creation.
- Expanded new-body mass range from `10^-8..10^-3` to `10^-10..10^-1` solar masses.
- Changed the speed slider to a logarithmic control with fractional slow motion.
- Added `Lock` camera dropdown to follow the Sun, Earth, or custom bodies.
- Updated tests, README, browser visualizer docs, and master decision log.

### Why

The sandbox needed more room for experimentation:

- Stationary masses help show gravity starting from rest.
- Wider mass choices let users create tiny particles or very heavy objects.
- Fractional speed makes it easier to inspect close interactions slowly.
- Camera lock keeps moving bodies visible instead of letting them drift off screen.

### How

Stationary creation works by letting `/api/add_body` default missing `vx` and `vy` values to zero.

The speed slider now stores a base-10 exponent:

```text
0.6 -> about 4 steps/frame
-1.0 -> 0.1 steps/frame, or about 1 step every 10 frames
```

The browser accumulates fractional steps until there is at least one whole physics step to request from Python.

Camera lock changes only the render transform:

```text
screen_position = world_position - focused_body_position
```

The physics state is unchanged.

### Verification

Latest test result:

```text
Ran 9 tests
OK
```

Manual API check:

```text
added bodies: 3
velocity: (0.0, 0.0)
mass: 1e-06
```

## 2026-05-29 - Physical Influence Clarified And UI Simplified

### What Changed

Updated the sandbox after noticing that user-added bodies could appear to have no effect:

- Changed the default new-body mass from `10^-6` to `10^-3` solar masses so perturbations are easier to see.
- Kept the full mass range wide enough to reach `10^-1` solar masses for dramatic influence.
- Added a regression test proving an added massive body changes an existing body's acceleration.
- Simplified the browser toolbar into a compact responsive grid.
- Shortened control labels so the UI fits better on screen.
- Documented the mass-scale explanation in `README.md` and `docs/phase1_browser_visualizer.md`.

### Why

The physics was already N-body: all preset bodies and user-added bodies are passed into the same acceleration calculation. The issue was scale. An Earth-mass body is about `3e-6` solar masses, so its effect on the Sun or another planet is real but visually subtle.

Raising the default mass makes the interactivity easier to understand while still preserving the actual gravity model.

### How

The existing force loop already sums all body pairs:

```text
for every pair of bodies:
    update acceleration of both bodies
```

The new test compares Earth's acceleration before and after adding a `0.1` solar-mass body nearby. The acceleration difference must be large enough to prove the new body is physically participating.

The UI was changed from a long wrapping toolbar into a compact grid with shorter labels:

- `New mass` became `Mass`
- `No initial velocity` became `Rest`
- `Free camera` became `Free`

### Verification

Latest test result:

```text
Ran 10 tests
OK
```

Manual acceleration influence check:

```text
added massive body changed existing body acceleration by 98.696...
```

## 2026-05-29 - Orbit Velocity Creation Added

### What Changed

Added orbit initialization for new bodies:

- Added `Orbit` checkbox in the browser UI.
- Added `Around` target selector populated from the current body list.
- Added server-side circular orbital velocity calculation.
- Added test coverage for computed orbital velocity.
- Updated README, browser visualizer docs, and master decision log.

### Why

Manually dragging a good orbital velocity is difficult. A user should be able to place a body and ask AstroRT to give it the velocity needed to orbit a selected object.

### How

When `Orbit` is enabled, the browser sends:

```json
{
  "x": 1.5,
  "y": 0.0,
  "mass": 0.000001,
  "orbitTarget": "Sun"
}
```

The server computes a prograde circular velocity around the target:

```text
speed = sqrt(G * (target_mass + new_body_mass) / distance)
```

Then it adds the target body's existing velocity, so orbiting a moving target is handled more correctly.

Important limitation: this is a two-body circular-orbit initialization inside a full N-body simulator. Other nearby bodies can still perturb the orbit afterward.

### Verification

Latest test result:

```text
Ran 11 tests
OK
```

HTTP smoke test:

```text
POST /api/add_body with orbitTarget=Sun -> 201
computed velocity: [0.0, 5.130183017340998]
```

## 2026-05-29 - Realtime Per-Body Physical Parameters Added

### What Changed

Added a compact `Bodies` readout to the browser visualizer.

Each body now reports:

- mass
- distance from origin
- speed
- acceleration vector
- acceleration magnitude
- kinetic energy
- angular momentum contribution

The server payload now includes these values for every body, and the browser renders them in a scrollable panel below the global metrics.

### Why

The simulator should be inspectable, not just visual. Realtime per-object parameters make it easier to understand what gravity is doing to each body and verify that added objects are physically active.

### How

The Python server computes the values from the authoritative simulation state:

- speed from `velocity.norm()`
- acceleration from the same pairwise gravity function used by the integrator
- kinetic energy from `0.5 * mass * speed^2`
- distance from `position.norm()`
- angular momentum from `mass * (x * vy - y * vx)`

The browser displays compact scientific notation so the UI stays readable across tiny and huge values.

### Verification

Latest test result:

```text
Ran 11 tests
OK
```

Manual payload check confirmed body telemetry fields are present for the Sun:

```text
mass, speed, accelerationMagnitude, kineticEnergy, distanceFromOrigin, angularMomentumZ
```

## 2026-05-29 - Elliptical Orbit Scenarios Added

### What Changed

Added elliptical orbit support to scenarios:

- `periapsis_speed(...)` helper using the vis-viva equation.
- `sun_earth_elliptical`
- `elliptical_inner_solar_system`
- tests proving elliptical Sun-Earth distance changes over the orbit
- tests proving periapsis speed is faster than the circular speed near 1 AU

### Why

The original scenarios were intentionally ideal circular starts. That is good for validating the integrator because circular motion makes drift easy to notice.

Real planetary orbits are usually elliptical, so AstroRT now includes scenarios where bodies start at periapsis with a physically appropriate velocity.

### How

The new helper uses:

```text
v^2 = G * (M + m) * (2/r - 1/a)
```

where:

- `r` is the periapsis distance
- `a` is the semi-major axis
- `M` is the central mass
- `m` is the orbiting mass

### Verification

Latest test result:

```text
Ran 13 tests
OK
```

Headless elliptical Sun-Earth check:

```text
Relative energy drift: 3.010518060488e-11
Relative Lz drift: 1.257138279851e-15
```

## 2026-05-29 - Draggable Collapsible HUD Added

### What Changed

Reworked the browser visualizer UI so it blocks less of the simulation:

- Converted the HUD into a compact dock.
- Added draggable HUD header.
- Added CSS resize support.
- Added collapsible sections for controls, metrics, and body telemetry.
- Made the `Bodies` panel collapsed by default.
- Added `Hide` and `Show UI` behavior.
- Added keyboard shortcut `H` to show/hide the HUD.
- Improved telemetry formatting so invalid values display as `--` instead of `NaN`.

### Why

The previous HUD covered too much of the simulation view, especially when the per-body parameter table was open. The simulator needs detailed instruments, but those instruments should be movable and collapsible so the user can inspect the actual motion.

### How

The HTML now uses `details` sections for collapsible panels. CSS gives the HUD fixed positioning, resize behavior, and a smaller default width. JavaScript handles dragging, collapse-all, hide/show, and keyboard toggling.

### Verification

Latest Python test result:

```text
Ran 13 tests
OK
```

The UI change is browser-facing, so the practical check is to run:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.server
```

Then confirm the HUD can be dragged, resized, collapsed, and hidden with `H`.

## 2026-05-29 - HUD Drag Fix And Eccentric Orbit Controls Added

### What Changed

Fixed HUD dragging and made elliptical motion more visible:

- Replaced pointer-capture HUD dragging with window-level pointer tracking.
- Added `Ecc` slider for orbit creation.
- Orbit mode now supports circular and elliptical starts.
- Added `comet_sun`, a high-eccentricity comet-like scenario.
- Reduced browser simulation `dt` to a quarter-day for better high-eccentricity sampling.
- Added tests for eccentric orbit speed and the comet scenario distance range.

### Why

The previous HUD drag could feel loose because pointer events were captured on one element while movement was listened for on another. Window-level tracking is more stable.

The realistic Earth-like ellipse looked almost circular because Earth really has a small eccentricity. For learning, we need both real-ish subtle ellipses and exaggerated ellipses that are visually obvious.

### How

Orbit creation now uses:

```text
speed = sqrt(G * (target_mass + new_body_mass) * (1 + eccentricity) / distance)
```

`Ecc = 0` gives circular speed. Larger eccentricity starts the body at periapsis of an elliptical orbit.

### Verification

Latest test result:

```text
Ran 15 tests
OK
```

Headless comet smoke check completed. High-eccentricity orbits can show larger energy drift with coarse time steps near periapsis, which is why the browser now uses a smaller default `dt`.

## 2026-05-29 - Blank Workspace And Cleaner Lab Scenarios Added

### What Changed

Added new scenario options:

- `blank`
- `single_sun`
- `sun_jupiter`
- `three_body_lab`

Changed the browser server default scenario from `sun_earth` to `single_sun`.

Updated Orbit target handling so `blank` safely shows no target until a body is added.

### Why

The original baseline simulations made it harder to debug orbit creation because existing bodies were already moving and perturbing the system. A blank workspace lets users build from nothing, and `single_sun` gives a clean central body for orbit experiments.

### How

`blank` returns an empty body list. `single_sun` returns one stationary Sun. The browser target dropdown now shows `No target` when there are no bodies.

### Verification

Latest test result:

```text
Ran 18 tests
OK
```

Manual checks:

```text
blank -> 0 bodies
single_sun -> 1 body named Sun
```

## 2026-05-29 - Observation UI Upgrades Added

### What Changed

Improved the browser visualizer as an observation tool:

- Added uniform `Zoom`.
- Added short professional scenario labels in the dropdown.
- Added click-to-focus on canvas bodies.
- Added click-to-focus on body table rows.
- Added `Focus` mode with `Off`, `Dim rest`, and `Solo`.
- Added toggleable `Edge` indicators for off-screen bodies.
- Reworked the body table header and row selection styling.
- Grouped UI controls more cleanly.

### Why

As simulations grow, bodies leave the frame and the UI can obscure the important motion. The user needs to zoom out for the full system, lock onto objects for close inspection, and see directional hints for off-screen bodies.

### How

Zoom is a display-only scale multiplier applied in `worldToScreen` and `screenToWorld`, preserving physical relative scale.

Edge indicators are drawn after bodies. If a body is outside the current viewport, an arrow is drawn at the nearest screen edge pointing toward it.

Focus mode uses the selected body from `Lock`:

- `Dim rest` lowers opacity for all other bodies.
- `Solo` skips drawing other bodies.

Clicking a body sets the lock target, enables dim focus if focus was off, and zooms in.

### Verification

Latest test result:

```text
Ran 18 tests
OK
```

JavaScript syntax check passed with `node --check web/app.js`.

### Verification

This was a documentation-only update. The correct command to use from PowerShell is:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## 2026-05-29 - Selected Body Editor Added

### What Changed

Added a `Selected Body` panel to the browser visualizer.

The selected body can now be edited without restarting the scenario:

- mass
- display radius
- velocity `Vx`
- velocity `Vy`
- clear selected trail
- remove selected body

Added backend endpoints:

- `POST /api/update_body`
- `POST /api/remove_body`
- `POST /api/clear_body_trail`

Added simulation helpers:

- `Simulation.find_body(...)`
- `Simulation.remove_body(...)`
- `Simulation.reset_metric_baseline()`

Added tests for editing, removing, and clearing trails.

### Why

The sandbox needs to support correction and experimentation after a body is
created. Real exploration means changing a body's mass or velocity and
watching the rest of the N-body system respond.

### How

The browser editor works on the body selected in `Lock`. When `Apply` is
pressed, the browser sends the new mass/radius/velocity values to Python.

Python updates the real simulation object, then resets the energy and angular
momentum baselines so the HUD drift values describe the edited system from
that moment onward.

Trail clearing is display-only. Removing a body changes physics and also
resets the metric baseline.

### Verification

Latest Python test result:

```text
Ran 21 tests
OK
```

JavaScript syntax check was not run in this WSL shell because `node` is not
installed here.

## 2026-05-30 - Physics Lab Interface Expansion

### What Changed

Expanded the Phase 1 browser visualizer into a richer local physics lab:

- Upgraded the selected-body inspector with name, color, position, velocity,
  mass presets, freeze, clone, delete, clear trail, and orbit-around-selected.
- Added backend diagnostics for center of mass, total momentum, center-of-mass
  velocity, closest pair, and maximum acceleration.
- Added visual overlays for net-force direction lines, center-of-mass marker,
  and closest-pair line.
- Added preset cards for common starter systems.
- Added timeline tools for stepping, rewinding recent browser frames, and
  downloading snapshots.
- Added `/about` as a lightweight portfolio/landing page.
- Added a real `POST /api/set_dt` endpoint so the warning action can reduce
  the actual integrator timestep instead of only slowing playback.
- Fixed timeline scrubbing so paused history frames are not immediately
  overwritten by live zero-step refreshes.

### Why

Phase 1 already had working physics, but the user experience needed to feel
like a lab: inspect objects, alter parameters, view important physical vectors,
and respond to numerical warnings without guessing.

The timestep fix matters because playback speed and physics timestep are not
the same thing. Slowing playback changes wall-clock speed. Reducing `dt`
changes numerical accuracy per step.

### How

Python remains the authoritative simulation layer. New inspector and timeline
actions call small JSON endpoints, then the browser redraws from the returned
state.

The visual overlays are display-only. They read backend-computed positions,
velocities, accelerations, and diagnostics, but they do not alter physics.

### Verification

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

Latest Python test result:

```text
Ran 29 tests
OK
```

JavaScript browser behavior still needs a real browser smoke test. This shell
does not have `node`, so `node --check web/app.js` was not run here.

## 2026-05-31 - Timestep Undo Controls Added

### What Changed

Added timestep controls beside `Halve dt`:

- `Double dt`
- `Reset dt`

The server state now reports `defaultDt`, and the backend has a new
`POST /api/reset_dt` route to restore the scenario's recommended browser
timestep.

### Why

`Halve dt` improves numerical sampling by making each physics step smaller, but
there should be a clear way to undo or reset that choice. Otherwise the user can
only keep making the simulation slower.

### How

`Halve dt`, `Double dt`, and `Reset dt` all change the real integrator timestep,
not just the playback speed slider.

- Smaller `dt`: more accurate around fast close passes, slower simulated years.
- Larger `dt`: faster simulated years, but more drift risk.
- Reset `dt`: returns to the scenario default.

### Verification

Added backend tests for `defaultDt` and timestep reset behavior.

Latest Python test result:

```text
Ran 30 tests
OK
```

## 2026-05-31 - Timeline History Starts At Run Beginning

### What Changed

Changed the browser timeline from a short rolling buffer into a full current-run
visual history.

- Removed the old 240-frame cap.
- Captured the first frame before the simulation advances.
- Reset timeline history when a scenario resets.
- Reset timeline history when a saved system is loaded.
- Updated the timeline label to show frame count and simulated time.

### Why

The timeline should let the user scrub from the beginning of the current run,
not only the most recent chunk. For normal scenario resets, that beginning is
`T=0`.

### How

The browser stores each live state it receives from Python in `stateHistory`.
When the user drags the timeline while paused, the browser displays a cloned
historic state instead of asking Python to advance the live simulation.

This is still a visual/browser replay, not a reverse integrator. When playback
continues, Python resumes from the real live state.

### Verification

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## 2026-05-31 - Custom Distance Measurements And Unit Readouts

### What Changed

Added a `Measurements` panel in the browser `View` tab:

- Distance unit selector: AU, million km, km.
- Mass unit selector: solar masses, Earth masses, Jupiter masses, kg.
- `Track pair` mode for clicking two bodies and tracking their live distance.
- Multiple tracked pairs at the same time.
- Per-pair remove buttons and a clear-all button.
- Green dashed measurement lines on the canvas.

Also changed the automatic `Closest` overlay to be off by default.

### Why

The closest-pair overlay is useful, but it answers only one automatic question:
"Which two bodies are nearest right now?" The user asked for a deliberate
measurement system where they can choose any bodies and watch their separation
in real time.

### How

The browser stores tracked pairs by body name and computes displacement from
the latest state payload:

```text
distance = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

The backend still runs physics in AU, years, and solar masses. Unit selectors
only convert displayed values.

### Verification

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## 2026-05-30 - Phase 1 Refinement Audit Added

### What Changed

Added `PHASE_1_REFINEMENT_AUDIT.md`.

### Why

Phase 1 is complete as a prototype, but it still needs a clear list of rough
edges before moving into the C++ engine phase.

### How

Ran:

- full Python unit tests
- headless scenario checks
- browser-timestep scenario sweep
- direct sandbox feature smoke test
- real HTTP endpoint smoke test

### Verification

Latest Python test result:

```text
Ran 25 tests
OK
```

The audit found the main refinement risks:

- chaotic close encounters need guardrails
- high-eccentricity scenarios need better timestep control
- browser JS still needs a proper local syntax/browser test path
- UI is functional but prototype-dense

## 2026-05-30 - Numerical Guardrails Added

### What Changed

Added scenario metadata and numerical health guardrails:

- scenario stability labels
- scenario notes
- smaller browser timestep for `comet_sun`
- smaller browser timestep plus softening for `three_body_lab`
- API warnings for sensitive/chaotic scenarios
- API warnings when energy or angular momentum drift rises
- visible HUD warning messages
- visible load/edit error messages instead of console-only warnings

Cleaned stale comments in `demo.py`.

### Why

The simulator should not silently look broken when a scenario is intentionally
chaotic or numerically sensitive. It should explain the risk and apply safe
Phase 1 defaults where possible.

### Verification

Latest Python test result:

```text
Ran 27 tests
OK
```

## 2026-05-30 - Browser Lab UI Upgrade

### What Changed

Improved the browser visualizer UI:

- Added HUD tabs: `Sim`, `Add`, `Inspect`, `View`, and `Data`.
- Added mouse wheel zoom around the cursor.
- Added manual camera pan by dragging empty canvas space.
- Added velocity vector overlay.
- Added acceleration vector overlay.

### Why

The Phase 1 browser tool had grown powerful but dense. Tabs make it easier to
use without covering the canvas, and vector overlays make the physics easier to
read visually.

### How

Tabs are display-only grouping around existing controls. Camera pan and wheel
zoom update frontend camera state only; they do not modify positions,
velocities, forces, or integrator behavior.

Velocity vectors are drawn from each body's current velocity. Acceleration
vectors are drawn from the backend acceleration payload.

### Verification

Latest Python test result:

```text
Ran 27 tests
OK
```

JavaScript browser behavior still needs real browser testing or Playwright.
This shell does not have `node`, so `node --check web/app.js` was not run here.

## 2026-05-30 - Focus Mode Default Preserved

### What Changed

Selecting a body no longer switches `Focus` from `Off` to `Dim rest`.

### Why

`Off` should behave as the true default. Selection, camera lock, and focus
visibility are separate controls.

### Verification

Latest Python test result:

```text
Ran 27 tests
OK
```

## 2026-05-30 - Phase 1 Completion Features Added

### What Changed

Added the remaining Phase 1 closure features:

- `Fit system`
- `Reset view`
- `Clear trails`
- `Save system`
- `Load system`
- `Export data`

Added backend APIs:

- `GET /api/export_system`
- `GET /api/export_data`
- `POST /api/load_system`
- `POST /api/clear_all_trails`

Added metric history tracking in `Simulation` so exported data includes energy
and angular momentum over time.

Added validation for invalid mass, velocity, and radius edits.

### Why

Phase 1 needed persistence and export before being considered complete.
Without save/load, created systems disappear when the server stops. Without
data export, Phase 4 AI has no clean bridge from simulation into datasets.

### How

`Save system` exports a compact rebuildable scenario JSON. `Load system`
replaces the running simulation with that JSON.

`Export data` produces an analysis payload with:

- units
- current state
- metric history
- body trails

View tools are frontend-only except trail clearing, which asks Python to clear
the authoritative trail lists.

### Verification

Latest Python test result:

```text
Ran 25 tests
OK
```

JavaScript syntax check was not run in this WSL shell because `node` is not
installed here.

## 2026-05-29 - Selected Body Editor Pause And Dirty-State Fix

### What Changed

Improved the selected-body editor interaction:

- Clicking into mass/radius/velocity fields now pauses the simulation.
- Typing marks the editor as dirty.
- Dirty editor values are protected from realtime telemetry refreshes.
- Pressing `Enter` inside an edit field applies the body edit.
- Added `setPaused(...)` so the pause state and pause/play button stay synced.

### Why

The editor was fighting the live simulation loop. The server sent a fresh state
every animation frame, and the UI could overwrite typed velocity or mass values
before `Apply` read them.

### How

`web/app.js` now tracks:

```text
editorDirty
editorBodyName
```

When the user edits a selected body's parameters, the app pauses and keeps the
draft values in the inputs. After `Apply`, Python updates the authoritative
simulation state and the editor syncs again.

### Verification

Latest Python test result:

```text
Ran 21 tests
OK
```

JavaScript syntax check was not run in this WSL shell because `node` is not
installed here.

## 2026-05-29 - Added Body Auto-Selection Fix

### What Changed

After creating a body in the browser:

- add mode now turns off automatically
- the new body becomes the selected/focused body
- the `Selected Body` editor is immediately populated with its mass, radius,
  and velocity

### Why

The editor technically worked, but the interaction was confusing. Because add
mode stayed active, clicking the new body still meant "place another body"
instead of "select this body for editing."

### How

Added a small `setAddMode(...)` helper in `web/app.js` so the add button label,
canvas cursor, and `addMode` flag always stay synchronized.

`addBody(...)` now remembers the previous body names, posts the new body to
Python, exits add mode, finds the newly added body in the returned state, and
calls `focusBody(...)` on it.

### Verification

Python tests still pass:

```text
Ran 21 tests
OK
```

JavaScript syntax check was not run in this WSL shell because `node` is not
installed here.

## 2026-05-31 - Force Overlay Made Visible

### What Changed

Changed the `Forces` overlay from faint short line segments into visible orange
net-force arrows.

### Why

The old force overlay was technically drawing, but it was too subtle and could
look like it did nothing at normal zoom levels.

### How

The browser now uses each body's backend acceleration and mass:

```text
net force magnitude = mass * acceleration magnitude
```

The arrow direction follows the acceleration direction. The arrow length is
screen-space scaled relative to the strongest net force in the current frame,
so it stays visible while zooming.

### Verification

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## 2026-05-31 - Close-Encounter Merge Guardrail Added

### What Changed

Added a browser simulation collision/merge guardrail for bodies that pass
extremely close together.

- `Simulation` now accepts `collision_distance`.
- The browser server uses a default close-encounter distance for interactive
  experiments.
- Bodies inside that distance merge into one body.
- The merge conserves total mass and linear momentum.
- Save/load and timeline restore now preserve the collision distance.
- Tests now verify that newly added bodies perturb existing accelerations and
  that very close browser bodies merge instead of passing through each other.

### Why

The force law was already pairwise and attractive, but Phase 1 used ideal
point masses. A point-mass body falling almost exactly through the Sun can hit
the Newtonian singularity near `r = 0`, receive a huge numerical velocity kick,
and appear to slingshot away unrealistically.

Real bodies have size. A body that falls into the Sun should collide/accrete,
not ghost through the center as a mathematical point. The new guardrail makes
browser experiments behave more like a sandbox with physical objects.

### How

Before and after each Velocity-Verlet step, the simulation checks for body
pairs closer than `collision_distance`.

When a pair merges:

```text
merged mass = mass_a + mass_b
merged position = center of mass of the pair
merged velocity = total momentum / total mass
```

That means the merge keeps the most important conservation rule for an
inelastic collision: momentum is not invented or destroyed.

### What This Does Not Mean

Gravity is still not repulsive. Bodies can still move away after a flyby if
they have enough speed to escape, because gravity slows them down but does not
magically stop them. The guardrail only fixes the unphysical point-mass
fly-through problem during extremely close encounters.

### Verification

Latest Python test result:

```text
Ran 35 tests
OK
```

## 2026-05-31 - Selected-Body Pull Overlay Added

### What Changed

Added a `Pull to lock` visual overlay in the View tab.

### Why

The existing `Forces` overlay shows the total/net force on each body. That is
physically correct, but it can hide smaller perturbations. For example, if a
new body is pulling on Earth while the Sun is still pulling harder, the net
arrow may point mostly toward the Sun.

The new overlay lets us isolate one contribution: the gravitational pull from
the currently locked body.

### How

The browser computes the pairwise acceleration contribution:

```text
a_from_locked = G * mass_locked * (locked_position - body_position) / distance^3
```

Then it draws purple arrows from visible bodies toward the locked body. This
does not change physics; it only makes one piece of the already-running
N-body force calculation easier to see.

### How To Use It

1. Click the new body, or select it in `View -> Lock`.
2. Turn on `Pull to lock`.
3. Keep `Forces` on if you want to compare selected-body pull against the net
   summed force.
