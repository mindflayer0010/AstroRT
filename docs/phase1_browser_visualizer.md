# Phase 1.1 Browser Visualizer

This document explains the first local browser version of AstroRT.

## 1. What We Built

Phase 1.1 adds a local web app:

- Python HTTP server
- JSON simulation API
- HTML page
- CSS interface styling
- JavaScript canvas renderer

Run it in PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.server
```

Then open:

```text
http://127.0.0.1:8000
```

## 2. Why This Exists

Before this step, AstroRT could run tests and print physics metrics in the terminal. That proves the core works, but it does not feel like a simulator yet.

The browser visualizer turns the project into a local interactive app while still keeping the architecture simple.

This also prepares the path for the future React/Next.js and Three.js frontend.

## 3. Server Flow

File: `src/astro_rt/server.py`

The server owns one `BrowserSimulationApp`.

That app owns:

- current scenario name
- time step
- running `Simulation`

The main API endpoints are:

```text
GET /api/state?steps=N
```

Advances the simulation by `N` steps and returns JSON.

```text
GET /api/reset?scenario=name
```

Restarts the simulation from a named scenario.

The server also serves:

- `/`
- `/index.html`
- `/app.js`
- `/styles.css`

## 4. Frontend Flow

Files:

- `web/index.html`
- `web/styles.css`
- `web/app.js`

The browser does not calculate gravity. It asks Python for the current state.

The loop is:

1. Request `/api/state?steps=N`.
2. Receive body positions, trails, colors, time, and drift metrics.
3. Draw the result on canvas.
4. Request the next animation frame.

This keeps the physics authoritative on the Python side.

## 5. Controls

Current controls:

- Pause/play.
- Reset.
- Scenario switch.
- Speed slider with fractional slow motion.
- Add body.
- Wider new body mass slider.
- No initial velocity toggle.
- Orbit velocity toggle and target selector.
- Eccentricity slider for visibly elliptical orbit creation.
- Orbital velocity calculator with circular speed, escape speed, period, and
  drag-speed error.
- Camera lock dropdown.
- Uniform zoom control.
- Mouse wheel zoom.
- Manual canvas pan by dragging empty space.
- Click-to-focus bodies.
- Hover cards for quick body inspection.
- Focus dim/solo mode.
- Edge indicators for off-screen bodies.
- Velocity and acceleration vector overlays.
- Net-force direction lines, center-of-mass marker, and closest-pair line.
- Custom distance trackers for multiple body pairs.
- Distance and mass unit selectors for readouts.
- Tabbed HUD sections.
- Help tab with quick-start controls and physics readout notes.
- Timeline controls for stepping, scrubbing/rewinding from the start of the
  current run, restoring the live simulation to a scrubbed frame, and snapshots.
- Preset cards for common scenario starts.
- Draggable/resizable HUD.
- Collapsible controls, metrics, and body panels.
- Hide/show UI toggle with the `H` key.
- Selected body editor for mass, velocity, display radius, trail clearing, and removal.
- View/data tools for fit-to-system, reset view, clear all trails, save/load, and export.

The speed slider controls how many physics steps the server runs per browser frame.

More steps per frame means the simulated years pass faster, but the server does more work. Values below 1 step/frame create slow motion by accumulating fractional steps across multiple frames.

The scenario list includes:

- `blank`: no bodies, fully from-scratch workspace
- `single_sun`: one central star, best for testing Orbit creation
- circular validation starts
- real-ish elliptical starts
- `comet_sun`: exaggerated comet-like ellipse
- `sun_jupiter`: clean giant-planet two-body setup
- `three_body_lab`: intentionally messy three-body experiment

Circular scenarios are useful for validation. Real Earth-like ellipses can still look almost circular because their eccentricities are small. Use `comet_sun` or the `Ecc` slider for a more obvious ellipse.

## Camera And Focus Tools

The visualizer has observation tools for reading the full system:

- `Zoom` changes the scale uniformly, so relative distances stay physically meaningful.
- Mouse wheel zooms around the cursor.
- Dragging empty canvas space pans the free camera.
- `Lock` follows a selected body.
- Clicking a body on the canvas selects it, locks the camera to it, and zooms in.
- Clicking a body row in the `Bodies` panel does the same.
- `Focus = Dim rest` keeps all bodies visible but reduces non-selected brightness.
- `Focus = Solo` hides non-selected bodies.
- `Edge` shows arrows at the screen edge for bodies outside the current view.
- `Velocity` shows blue velocity arrows.
- `Accel` shows yellow acceleration arrows.
- `Forces` shows orange net-force arrows. Direction follows acceleration, and
  arrow length is scaled by relative `mass * acceleration` in the current frame.
- `COM` marks the center of mass.
- `Closest` draws a line between the automatically detected closest pair of bodies.
- `Measurements` lets you click two bodies to track their separation live.

These are display tools only. They do not change the simulation state.

## Measurements And Units

The closest-pair overlay is automatic: it always asks "which two bodies are
nearest right now?" That is useful for close-encounter warnings, but it is not
the same as a custom measurement.

The measurement tool is user-chosen:

1. Open the `View` tab.
2. Open `Measurements`.
3. Choose a distance unit and mass unit.
4. Click `Track pair`.
5. Click the first body, then the second body.

The app keeps that pair in the measurement list and draws a green dashed line
between the bodies. You can add multiple pairs, remove individual pairs, or
clear all pairs. The distances update while the simulation runs and while it is
paused or scrubbed on the timeline.

Current distance readout units:

- AU
- million km
- km

Current mass readout units:

- solar masses
- Earth masses
- Jupiter masses
- kg

The physics still runs internally in AU, years, and solar masses. Unit selectors
only change display/readout conversion.

## HUD Tabs

The HUD is grouped into compact tabs:

- `Sim`: playback, scenario, speed, and health metrics.
- `Add`: body creation controls.
- `Inspect`: body table and selected-body editor.
- `View`: camera, focus, trails, and vector overlays.
- `Data`: save, load, and export.

Tabs keep the simulator visible while preserving all Phase 1 controls.

## Object Inspector

The selected-body inspector now supports:

- name edits
- color picker
- mass presets for asteroid, Earth, Jupiter, and Sun
- position `X/Y`
- velocity `Vx/Vy`
- display radius
- freeze velocity
- clone body
- delete body
- clear selected trail
- use selected body as the orbit target for the next added body

This keeps system editing inside the browser instead of forcing a scenario reset.

## Timeline And Shortcuts

Timeline tools:

- `Step`: advance exactly one physics step while paused.
- `Timeline`: scrub visual frames stored since the beginning of the current run.
- `Rewind`: step backward through the current run history.
- `Restore here`: replace the live Python simulation with the currently
  scrubbed timeline frame.
- `Snapshot`: download the current system JSON.
- `Halve dt`: halves the actual physics timestep as a quick response to drift
  or close-encounter warnings.
- `Double dt`: increases the actual physics timestep again after experimenting.
- `Reset dt`: restores the current scenario's recommended browser timestep.

`Halve dt` is intentionally different from the speed slider. The speed slider
changes how many steps run per animation frame. The timestep changes how much
simulated time each physics step covers, so smaller `dt` can improve numerical
accuracy when bodies move quickly near each other. Larger `dt` makes simulated
time advance faster per step, but it can increase drift in sensitive systems.

The timeline starts fresh when a scenario is reset or a saved system is loaded.
For a normal scenario reset, the first timeline frame is `T=0`.

`Restore here` is the bridge between visual replay and real simulation state.
Scrubbing alone only changes what the browser displays. Restoring sends that
saved frame back to Python as a loadable system, resets metric baselines, and
continues the live simulation from that moment.

Keyboard shortcuts:

- `H`: show/hide HUD
- `F`: fit system
- `R`: reset view
- `.`: step once
- `?`: open Help
- double-click a body: select and open inspector

## Help Tab

The Help tab is the in-app reference for Phase 1:

- quick-start workflow
- mouse controls
- keyboard shortcuts
- `dt`, energy drift, vector, and center-of-mass explanations

It is intentionally compact so the simulator can teach the basics without
turning into a separate documentation page.

## Selected Body Editing

The `Selected Body` panel edits whichever object is currently selected in
`Lock`. You can select an object by clicking it on the canvas or by clicking
its row in the `Bodies` panel.

What it edits:

- `Name`: display and selection name for the body.
- `Color`: display color for the body.
- `Mass`: physical mass in solar masses. This changes gravity.
- `X` and `Y`: position in AU. This can teleport a body for sandbox setup.
- `Vx` and `Vy`: velocity components in AU/year. This changes motion.
- `Radius`: display size in pixels. This does not change gravity.
- mass presets: asteroid, Earth, Jupiter, and Sun.
- `Freeze`: sets velocity to zero.
- `Clone`: duplicates the body with a small offset.
- `Orbit around`: prepares the Add tab to create a new body orbiting the selected body.
- `Clear trail`: removes only the drawn history.
- `Remove`: deletes the body from the current simulation.

Why it matters:

Adding bodies is useful, but editing them makes the app a real sandbox. If an
orbit is too fast, a planet is too light, or a marker is visually too small,
you can correct the current system instead of restarting.

How it works:

The browser sends JSON to Python endpoints:

```text
POST /api/update_body
POST /api/remove_body
POST /api/clear_body_trail
POST /api/clone_body
POST /api/freeze_body
POST /api/set_dt
POST /api/reset_dt
```

Python still owns the real state. After physical edits such as mass or
velocity, the simulation resets its energy and angular-momentum baseline so
future drift is measured from the edited system.

How to test it manually:

1. Start the visualizer.
2. Click a body.
3. Change mass or velocity in `Selected Body`.
4. Press `Apply`.
5. Watch the selected body and nearby bodies respond.

Editing behavior:

- Focusing a mass/radius/velocity field pauses the simulation.
- Typing into a field marks the editor as dirty.
- Dirty editor values are not overwritten by live telemetry refreshes.
- Pressing `Enter` in a field also applies the edit.
- After `Apply`, Python updates the real body and the editor syncs to the new
  authoritative state.

Future phase supported:

This is the first version of the property inspector we will later expand in
the React/Next.js interface.

## Guided Add Body

The Add tab has a `Kind` selector:

- Custom
- Asteroid
- Earth-like
- Jupiter-like
- Star

Choosing a kind sets the mass slider, display radius, color, and helper text.
The physics still uses the same N-body gravity path; this is a usability layer
that makes common choices faster and less guessy.

Manual mode uses click-drag velocity. `Rest` drops a body with zero initial
velocity. `Orbit` asks Python to compute a two-body orbital start around the
selected target.

The Add tab also shows an orbital calculator:

- `radius`: current distance from the selected target.
- `circular`: speed needed for a circular orbit.
- `escape`: speed needed to escape from that radius.
- `period`: approximate orbital period for the selected radius/eccentricity.
- `drag speed`: speed implied by the current click-drag vector.
- `error`: drag speed compared with the required circular/eccentric start.

The key formulas are:

```text
circular speed = sqrt(G * (M + m) / r)
escape speed   = sqrt(2 * G * (M + m) / r)
period         = 2*pi*sqrt(a^3 / (G * (M + m)))
```

These are two-body estimates. After creation, AstroRT still runs the full
N-body simulation.

## Hover Cards

Hovering a body shows a compact readout:

- mass in the selected mass unit
- distance from origin in the selected distance unit
- distance to the focused body, when applicable
- speed
- acceleration magnitude

This makes quick inspection possible without opening the inspector table.

## View And Data Tools

The `View + Data` panel closes the main Phase 1 usability gaps.

What it includes:

- `Fit system`: returns to free camera and chooses a zoom that shows the full current system.
- `Reset view`: returns to free camera at default zoom.
- `Clear trails`: removes all orbit trails without changing positions or velocities.
- `Save system`: downloads a JSON file with the current bodies.
- `Load system`: reloads a previously saved JSON system.
- `Export data`: downloads a JSON analysis payload with units, current state, metric history, and body trails.

Why it matters:

Saving/loading means interesting systems are no longer temporary. Exporting data
creates the first bridge from Phase 1 physics into later ML work.

How it works:

The browser calls these server APIs:

```text
GET  /api/export_system
GET  /api/export_data
POST /api/load_system
POST /api/clear_all_trails
```

`Save system` is for reconstructing a simulation. `Export data` is for
analysis, plotting, and future dataset-generation experiments.

## HUD Layout

The HUD is designed to stay out of the way of the simulation:

- Drag it by the `AstroRT` header.
- Resize it from the bottom-right corner.
- Collapse or expand all panels with `Collapse`.
- Open/close individual panels using their section headers.
- Hide the whole HUD with `Hide`.
- Press `H` to show or hide the HUD quickly.

The `Bodies` panel starts collapsed because it contains the most data and can block the canvas if left open on smaller screens.

## 6. Adding Bodies

Click `Add body`, then click and drag on the canvas.

What happens:

1. The drag start point becomes the new body's position.
2. The drag direction and length become the new body's initial velocity.
3. The new body mass comes from the `New mass` slider.
4. The browser sends that data to Python with `POST /api/add_body`.
5. Python adds the body to the running `Simulation`.
6. The energy and angular momentum baselines reset to the edited system.
7. The browser exits add mode and selects the new body for editing.

The browser still does not run physics. It only sends the new body's starting state.

This is our first sandbox-editing feature.

Every body in the simulation affects every other body through the same N-body gravity loop. A newly added body can look ineffective when its mass is small compared with the Sun. For visible perturbations, raise the mass slider toward `1e-2` or `1e-1` solar masses.

While dragging, the visualizer shows:

- an arrow for the initial velocity direction
- approximate launch speed in AU/year
- selected mass in solar masses

If `No initial velocity` is enabled, the new body is added with velocity `(0, 0)`. That lets you drop a mass into the system and watch gravity begin accelerating it from rest.

## 7. Orbit Creation

If `Orbit` is enabled, the server ignores the drag velocity and computes orbital velocity around the body selected in `Around`.

With `Ecc = 0`, this is circular. With higher `Ecc`, the body starts at periapsis of an elliptical orbit. The formula is:

```text
speed = sqrt(G * (target_mass + new_body_mass) * (1 + eccentricity) / distance)
```

The velocity direction is perpendicular to the radius from the target to the new body. The target body's current velocity is also added, so orbiting a moving body works better than assuming the target is fixed in space.

This gives a strong starting orbit, but it is still only a local two-body approximation. AstroRT then continues with full N-body gravity, so other nearby bodies can perturb the orbit. Very high eccentricity or very close periapsis needs smaller time steps for high accuracy.

In `blank`, there is no orbit target until you add a body. A good flow is:

1. Select `blank`.
2. Turn on `Rest`.
3. Add a massive body near the center.
4. Turn off `Rest`, enable `Orbit`, choose that body in `Around`.
5. Add another body away from it.

## 8. Camera Lock

The `Lock` dropdown changes the camera center.

Options include:

- Free camera
- scenario bodies such as Sun and Earth
- user-added bodies

Locking does not change physics. It only changes how the canvas converts world coordinates into screen coordinates, so the selected object stays near the center while it moves.

## 9. Metrics

The visualizer displays:

- simulation time
- relative energy drift
- relative angular momentum drift
- scenario stability label
- numerical health warnings
- per-body mass
- per-body distance from origin
- per-body speed
- per-body acceleration magnitude
- per-body kinetic energy
- per-body angular momentum contribution

These numbers matter because orbital simulations can look good while slowly becoming physically wrong.

Small drift means the current integrator and time step are behaving well for the scenario.

Warnings appear for sensitive scenarios and when drift crosses thresholds. This
is especially important for comet-like and chaotic close-encounter setups,
where fixed timesteps can become inaccurate near fast periapsis passages or
near-collisions.

The per-body panel is useful for inspecting individual objects in realtime. For example, a body with no initial velocity should show speed increasing as gravity accelerates it. A body farther from the Sun usually has a lower circular orbital speed than one close to the Sun.

## Net Force vs Pull From One Body

The `Forces` overlay shows the net force on each body:

```text
net force = sum of all gravitational pulls from all other bodies
```

That is why a planet's force arrow may still point mostly toward the Sun even
after a new massive body is added. The new body is pulling too, but the Sun can
still dominate the vector sum.

The `Pull to lock` overlay answers a narrower question:

```text
how much is the locked body alone pulling on every other visible body?
```

To inspect a new body, click it or select it in `Lock`, then turn on `Pull to
lock`. Purple arrows will start from the other bodies and point toward the
locked body. This is a visual teaching tool; it does not change the physics.

## 10. What This Is Not Yet

This is not the final hosted web app yet.

It does not have:

- React
- Three.js
- FastAPI
- database saves
- user accounts
- public deployment

Those come later. This step is the smallest useful bridge between the physics engine and a future web product.

## 11. How We Test It

Run:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

The browser visualizer tests check:

- the API payload includes the fields the frontend needs
- stepping advances simulation time
- reset can switch scenarios
- sensitive scenarios expose timestep/softening guardrails
- drift warnings appear when energy error is high
- adding a body appends it and resets the metric baseline
- added bodies keep the selected custom mass
- adding a body can default to zero initial velocity
- a newly added massive body changes an existing body's acceleration
- orbit mode computes circular orbital velocity around the selected target
- state payload includes realtime per-body physical parameters
- selected body edits can update mass, velocity, and display radius
- selected bodies can be removed
- selected body trails can be cleared without changing physics
- all trails can be cleared
- systems can be exported and loaded back
- data export includes units, metric history, and body trails
- browser close-encounter guard merges bodies that pass inside the merge radius

## Rest, Flybys, And Collisions

`Rest` means zero initial velocity. It does not pin a body in place. Gravity
still accelerates that body immediately.

If a body has more than escape speed, it can pass by the system and keep moving
away. That is not repulsion; gravity is still pulling, but the object has enough
kinetic energy to escape.

The unrealistic behavior we guard against is a point-mass fly-through near
`r = 0`. Pure point masses have infinite acceleration at exact overlap, and a
fixed timestep integrator can inject fake energy there. The browser simulation
therefore uses a Phase 1 merge guardrail: bodies inside the close-encounter
radius merge into one body while conserving mass and linear momentum.

This is not final collision physics. It is a practical guardrail so a body that
falls into the Sun behaves like an accretion/merge event instead of a numerical
slingshot.
