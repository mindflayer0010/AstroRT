# AstroRT Phase 1 Report

Phase 1 is complete as of 2026-05-30.

## Goal

Build a clear Python research prototype for 2D N-body orbital dynamics before
moving the performance-critical engine to C++.

## What We Built

- A `Body` model with mass, position, velocity, display radius, color, and trail.
- Pairwise Newtonian gravity in astronomical units.
- Velocity-Verlet integration.
- Energy and angular momentum tracking.
- Reusable scenarios, including blank, single-star, circular, elliptical, comet, binary, and three-body starts.
- A headless metrics demo.
- A local browser visualizer served by Python's standard library.
- Interactive add/edit/remove body tools.
- Rest and orbit initialization modes.
- Per-body realtime physical parameters.
- Camera lock, focus modes, zoom, edge indicators, fit-to-system, and reset view.
- Tabbed HUD, mouse-wheel zoom, manual pan, and vector overlays.
- Net-force direction lines, center-of-mass marker, and closest-pair marker.
- Custom distance measurement pairs with selectable distance and mass readout units.
- A fuller object inspector with name, color, position, mass presets, freeze,
  clone, delete, trail clearing, and orbit-around-selected shortcuts.
- Timeline tools for stepping, scrubbing/rewinding from the beginning of the
  current run, restoring the live simulation to a scrubbed frame, snapshots,
  and actual timestep reduction.
- Hover info cards and guided Add Body presets.
- Orbital velocity calculator for circular speed, escape speed, period, and drag-speed error.
- Browser close-encounter merge guardrail for point-mass fly-throughs.
- In-app Help tab for controls and physics readout explanations.
- Preset cards and a lightweight `/about` portfolio page.
- Save/load current system JSON.
- Export current state, metric history, units, and trails for analysis.
- Scenario stability notes, drift warnings, and timestep/softening guardrails
  for sensitive setups.
- A development log and learning docs.

## What We Learned

Gravity becomes code by summing each other body's acceleration contribution.
Every body affects every other body, so adding a massive new object should
perturb existing motion.

Velocity-Verlet is a good first orbital integrator because it has much better
long-term energy behavior than a naive Euler step.

Energy drift and angular momentum drift are health checks. A simulation can
look visually smooth while slowly becoming physically wrong.

Circular orbits are useful for validation. Elliptical and comet-like scenarios
are better for learning because their distance changes are easier to see.

## Current Units

- distance: AU
- mass: solar masses
- time: years
- velocity: AU/year

With these units, `G = 4 * pi^2`, so an Earth-like body at `1 AU` with speed
`2 * pi AU/year` orbits a one-solar-mass star in about one year.

## How To Run

Browser visualizer:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.server
```

Open:

```text
http://127.0.0.1:8000
```

Headless validation:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.demo --headless --scenario sun_earth --years 1
```

Tests:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

## Verification

Latest automated test result:

```text
Ran 35 tests
OK
```

The tests cover core physics, scenario sanity, API payload shape, body creation,
orbit initialization, body editing/removal, trail clearing, save/load, data
export, invalid mass rejection, added-body perturbation, and close-encounter
merging.

## Known Limitations

- The simulator is 2D.
- The force calculation is exact pairwise `O(N^2)`, so it is not ready for very large systems.
- The browser UI is a Phase 1 local tool, not the final React/Three.js product.
- Exported data is JSON for readability, not an optimized ML dataset format.
- Orbit initialization is a two-body approximation; the simulation continues as full N-body after creation.
- Very close encounters and highly eccentric orbits may need smaller time steps.
- The browser merge guardrail is a simple inelastic collision model, not a
  final collision/accretion/fragmentation system.
- Chaotic scenarios are guarded and labeled, but high-fidelity close-encounter
  handling belongs in later engine work.

## Phase 2 Handoff

Phase 2 should start the C++ physics core using the validated Phase 1 behavior
as the reference.

Recommended C++ first modules:

- `Vec2` or `Vec3`
- `Body`
- pairwise gravity
- Velocity-Verlet integrator
- `Simulation`
- energy and angular momentum metrics
- tests matching the Python Sun-Earth conservation checks

Python Phase 1 remains the teaching, visualization, and reference prototype.
