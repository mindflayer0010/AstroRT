# Phase 1 Refinement Audit

Date: 2026-05-30

## Test Pass Summary

Automated tests after refinement:

```text
Ran 27 tests
OK
```

Headless scenario checks:

- `sun_earth`: relative energy drift `1.116866038484e-13` over ~1 year.
- `binary_stars`: relative energy drift `1.083495116786e-13` over ~1 year.
- `comet_sun`: relative energy drift `1.082921693726e-02` over ~1 year with the coarse headless timestep.

Browser timestep scenario sweep:

```text
binary_stars                  energyDrift=4.140e-15
blank                         energyDrift=0.000e+00
comet_sun                     energyDrift=6.754e-04
elliptical_inner_solar_system energyDrift=3.692e-06
inner_solar_system            energyDrift=6.747e-11
single_sun                    energyDrift=0.000e+00
sun_earth                     energyDrift=6.516e-15
sun_earth_elliptical          energyDrift=1.829e-15
sun_jupiter                   energyDrift=8.619e-12
three_body_lab                energyDrift=8.460e+03
```

HTTP smoke check:

- `/`
- `/app.js`
- `/styles.css`
- `/api/state`
- `/api/export_system`
- `/api/export_data`
- `/api/add_body`
- `/api/update_body`
- `/api/clear_all_trails`
- `/api/load_system`
- `/api/remove_body`

All checked endpoints returned successful HTTP statuses.

## What Still Needs Refinement

### 1. Chaotic/Close-Encounter Scenarios Need More Physics Later

Fixed for Phase 1: `three_body_lab` now has scenario metadata, a smaller
browser timestep, softening, and visible warnings.

Still future work: this is not a replacement for real close-encounter physics.
Phase 2/3 should add better timestep control, collision/merge handling, or a
more robust integrator path.

Recommended next refinement:

- Mark it as an unstable/chaotic lab scenario.
- Add a smaller default timestep for close-encounter scenarios.
- Add optional softening or collision/merge handling.

### 2. High-Eccentricity Orbits Still Need Adaptive Time-Step Control

Fixed for Phase 1: `comet_sun` now runs with a smaller browser timestep and a
visible sensitivity warning. Comets still move fastest near periapsis, so fixed
timesteps are least accurate exactly where the motion is hardest.

Recommended next refinement:

- Add a smaller timestep preset.
- Add adaptive stepping later.
- Show a warning when energy drift exceeds a threshold.

### 3. Browser JavaScript Is Not Fully Tool-Tested Here

The Python tests and HTTP endpoints pass. However, this shell does not have
`node`, so `node --check web/app.js` could not be run during this audit.

Recommended next refinement:

- Install Node locally or add a lightweight JS check command.
- Later use Playwright for actual browser interaction tests.

### 4. UI Is Functional But Still Prototype-Level

The browser app has many controls in a compact HUD. It works, but it can still
feel dense or awkward.

Recommended next refinement:

- Split controls into clearer tabs.
- Continue improving inline error messages.
- Add a visible "paused for editing" state near the main controls.
- Add keyboard shortcuts for fit view, reset view, and clear trails.

### 5. Save/Load Is Useful But Minimal

Save/load currently handles the current system body state. It does not include
all UI state, camera state, selected body, or complete trajectory history.

Recommended next refinement:

- Decide whether saved systems should include UI/camera state.
- Add schema validation and clearer load errors.
- Add a human-readable scenario description field.

### 6. Export Data Is Readable, Not ML-Ready

JSON export is good for learning and inspection. It is not yet an efficient ML
dataset format.

Recommended next refinement:

- Add CSV export for quick plotting.
- Add NPZ/Parquet later for larger datasets.
- Add explicit trajectory arrays per body with aligned timestamps.

### 7. Headless Demo Still Has Stale Comments

`src/astro_rt/demo.py` has old comments/TODOs about zoom/pan coming later and
the demo not being a sandbox editor. The browser app now has those features,
so the comments should be revised.

Recommended next refinement:

- Clean stale comments.
- Clarify that `demo.py` is now the simple headless/Pygame path, while
  `server.py` is the richer browser sandbox.

### 8. Phase 1 Is Complete, But Not Production-Polished

Phase 1 is complete as a reference prototype. It is not complete as a polished
product.

Recommended next refinement:

- Do a UI hardening pass.
- Add browser interaction tests.
- Add drift warnings.
- Add close-encounter handling.

## Quick Conclusion

Phase 1 is strong enough to serve as the reference for Phase 2 C++ work, with
the biggest numerical hazards now labeled and guarded in the browser app.

Before or during Phase 2, the most valuable refinement is not adding more UI
features. It is adding simulation guardrails: timestep controls, drift warnings,
and close-encounter handling.
