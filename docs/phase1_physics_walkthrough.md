# Phase 1 Physics Walkthrough

This walkthrough explains the first AstroRT physics prototype file by file. The goal is not just to know what the code does, but to understand the physics idea behind each part.

## 1. Big Picture

Phase 1 simulates a tiny 2D universe.

Each body has:

- mass
- position
- velocity

At every time step:

1. Gravity calculates acceleration on each body.
2. The integrator advances positions and velocities.
3. Metrics measure whether the simulation is staying physically trustworthy.

The current flow is:

```text
scenario -> Simulation -> velocity_verlet_step -> accelerations -> metrics
```

## 2. `constants.py`

File: `src/astro_rt/constants.py`

This file defines the gravitational constant used by the simulator:

```python
G = 4.0 * pi * pi
```

### What This Means

In real SI units, gravity uses:

```text
G = 6.67430e-11 m^3 kg^-1 s^-2
```

That value is correct, but awkward for a beginner simulation because planets are huge, distances are huge, and numbers become hard to inspect.

So Phase 1 uses normalized astronomy units:

- distance: astronomical units
- mass: solar masses
- time: Earth years

In these units, an Earth-like planet at `1 AU` moving at `2*pi AU/year` orbits a `1 solar mass` star in about one year.

### Why We Do This

It makes the code easier to understand and debug.

Instead of asking:

```text
Is 29780 m/s correct?
```

we can ask:

```text
Is Earth moving at about 2*pi AU/year?
```

That directly connects to circular motion.

### Circular vs Elliptical Starts

The first scenarios used circular-orbit speeds on purpose. Circular starts are idealized, but they are excellent for validating the integrator because a stable circle makes drift easy to spot.

Real planetary orbits are usually elliptical. AstroRT now also includes elliptical presets that start bodies at periapsis using the vis-viva equation:

```text
v^2 = G * (M + m) * (2/r - 1/a)
```

where:

- `r` is the current distance from the central body
- `a` is the semi-major axis
- `M` is central mass
- `m` is orbiting mass

At periapsis, the body is closest to the central mass and moving fastest. At apoapsis, it is farthest and moving slowest.

## 3. `vector.py`

File: `src/astro_rt/vector.py`

This file defines `Vec2`, a tiny 2D vector type.

### What A Vector Is

A vector is a quantity with direction and size.

For AstroRT:

- position is a vector
- velocity is a vector
- acceleration is a vector
- force direction is a vector

Example:

```text
position = (1.0, 0.0)
velocity = (0.0, 6.283)
```

That means the body is 1 AU to the right of the origin and moving upward.

### Why We Made Our Own `Vec2`

The current environment did not have `pip`, `ensurepip`, or NumPy installed. A pure-Python `Vec2` keeps the prototype runnable immediately.

It also prepares us for C++, because later we will likely write a similar `Vec2` or `Vec3` type in the C++ engine.

### Important Methods

- `__add__`: vector addition
- `__sub__`: vector subtraction
- `__mul__`: scalar multiplication
- `__truediv__`: scalar division
- `dot`: dot product
- `norm`: vector length

The dot product is used to calculate squared distance:

```text
distance_squared = delta dot delta
```

For `delta = (x, y)`:

```text
delta dot delta = x*x + y*y
```

Then:

```text
distance = sqrt(x*x + y*y)
```

## 4. `body.py`

File: `src/astro_rt/body.py`

This file defines `Body`.

### What A Body Is

A body is one object in the simulation. It can be:

- a star
- a planet
- a moon
- an asteroid
- later, a spacecraft

Current fields:

- `name`: human-readable label
- `mass`: gravitational mass
- `position`: current location
- `velocity`: current movement
- `radius`: display size
- `color`: display color
- `trail`: past positions for visualization

### Why This Shape Matters

Physics simulation starts with state.

For Phase 1, a body's state is:

```text
position + velocity
```

Mass affects how strongly the body attracts other bodies. Position controls distance and direction. Velocity controls how the body moves through space.

## 5. `forces.py`

File: `src/astro_rt/forces.py`

This file calculates gravitational acceleration.

### The Physics Equation

Newtonian gravity says:

```text
F = G * m1 * m2 / r^2
```

But for simulation, we usually want acceleration:

```text
F = m * a
```

So:

```text
a = F / m
```

For body `i`, acceleration caused by body `j` becomes:

```text
a_i = G * m_j * direction / distance^2
```

In vector form:

```text
a_i = G * m_j * (r_j - r_i) / |r_j - r_i|^3
```

### What The Code Does

For every pair of bodies:

1. Calculate `delta`, the vector from body `i` to body `j`.
2. Calculate distance squared.
3. Calculate distance.
4. Calculate direction divided by distance squared.
5. Add acceleration to body `i`.
6. Add the equal/opposite mass-weighted effect to body `j`.

### Why Pairwise Gravity Is O(N^2)

If there are `N` bodies, every body interacts with every other body.

For 10 bodies, that is manageable.

For 10,000 bodies, it becomes too slow.

That is why future phases include Barnes-Hut and possibly AI-assisted far-field approximation.

## 6. `integrators.py`

File: `src/astro_rt/integrators.py`

This file advances the simulation through time.

### Why We Need An Integrator

Gravity tells us acceleration right now.

But the simulator needs to answer:

```text
Where will everything be after a small amount of time?
```

That is the integrator's job.

### Velocity-Verlet

Velocity-Verlet does one step like this:

1. Compute current acceleration.
2. Move position using current velocity and acceleration.
3. Compute new acceleration at the new position.
4. Update velocity using the average of old and new acceleration.

In plain language:

```text
Use gravity now to move the body.
Then check gravity again.
Then update speed using both gravity measurements.
```

### Why Not Simple Euler?

Euler integration does something like:

```text
position = position + velocity * dt
velocity = velocity + acceleration * dt
```

That is easy, but it often adds or removes energy over time. In orbital simulations, that can make planets spiral inward or fly away.

Velocity-Verlet is still simple, but it behaves much better for orbital motion.

## 7. `metrics.py`

File: `src/astro_rt/metrics.py`

This file checks whether the simulation is physically sane.

### Kinetic Energy

Kinetic energy is energy of motion:

```text
KE = 0.5 * mass * speed^2
```

Fast or massive bodies have more kinetic energy.

### Potential Energy

Gravitational potential energy is:

```text
PE = -G * m1 * m2 / distance
```

It is negative because gravity is attractive.

### Total Energy

Total energy is:

```text
total = kinetic + potential
```

For an ideal isolated orbital system, total energy should stay constant.

In a numerical simulation, it will not be perfectly constant, but the drift should be small.

### Angular Momentum

Angular momentum measures rotational motion around the origin.

In 2D, we track the z-component:

```text
Lz = mass * (x * vy - y * vx)
```

For a stable isolated orbit, angular momentum should also stay nearly constant.

## 8. `scenarios.py`

File: `src/astro_rt/scenarios.py`

This file gives us repeatable starting systems.

Current scenarios:

- `sun_earth`
- `sun_earth_elliptical`
- `binary_stars`
- `inner_solar_system`
- `elliptical_inner_solar_system`

### Why Scenarios Matter

Scenarios are test fixtures for physics.

If we change the integrator or gravity code, we can rerun the same scenarios and compare:

- Does energy drift get worse?
- Does angular momentum drift stay small?
- Does Earth still return near its starting position?
- Does an elliptical body change distance from the Sun over the orbit?

## 9. `simulation.py`

File: `src/astro_rt/simulation.py`

This file wraps the running state.

`Simulation` owns:

- the bodies
- the time step
- the current simulation time
- the softening value
- initial energy
- initial angular momentum

### What `step()` Does

`step()` advances the simulation by one or more integrator steps.

After each step, it records trail points for visualization.

### What `snapshot()` Does

`snapshot()` returns current metrics:

- time
- total energy
- angular momentum

This is useful for demos, tests, and later dashboards.

## 10. `demo.py`

File: `src/astro_rt/demo.py`

This file lets us run the simulator.

### Headless Mode

Headless mode prints metrics without opening a window.

PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.demo --headless --scenario sun_earth --years 1
```

This is useful for quick validation.

### Viewer Mode

Viewer mode tries to use Pygame:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.demo --scenario sun_earth
```

If Pygame is not installed, it falls back to headless mode.

## 11. `tests/test_phase1_physics.py`

File: `tests/test_phase1_physics.py`

These tests prove the first physics slice behaves correctly.

Run in PowerShell:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

Current checks:

- Energy drift stays tiny for Sun-Earth.
- Angular momentum drift stays tiny for Sun-Earth.
- Earth returns near its starting position after about one year.
- Pairwise acceleration respects Newton's third law in mass-weighted form.
- Inner Solar System center of mass is finite.

## 12. What The Latest Test Result Means

You ran:

```powershell
$env:PYTHONPATH="src"; python -m unittest discover -s tests
```

And got:

```text
Ran 4 tests in 0.035s
OK
```

That means the current physics prototype passes its first validation gate.

You also ran:

```powershell
$env:PYTHONPATH="src"; python -m astro_rt.demo --headless --scenario sun_earth --years 1
```

And got energy drift around:

```text
1.1e-13
```

That is excellent for this starter scenario.

## 13. Next Concepts To Learn

Before adding new features, the most useful next concepts are:

- why `dt` controls accuracy and speed
- why energy drift is a warning signal
- how Euler differs from Velocity-Verlet
- how orbit trails reveal stability
- why exact N-body gravity gets slow as body count grows
