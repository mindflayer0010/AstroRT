# AstroRT - Astro Real-Time Dynamics Lab

AstroRT is a long-term flagship project for learning and building real-time orbital simulation, AI-assisted prediction, and space-science visualization. This file is the single source of truth for the project plan.

Implementation notes and change-by-change explanations are tracked in `DEVELOPMENT_LOG.md`.

## 1. Vision

AstroRT should become an AI-powered real-time space physics simulator: part orbital mechanics sandbox, part research lab, part educational tutor, and part portfolio-grade engineering system.

The long-term experience should feel like a serious scientific version of a space sandbox:

- Create planets, moons, asteroids, spacecraft, and custom systems.
- Simulate N-body gravity in real time.
- Visualize orbit trails, force vectors, velocity vectors, energy drift, and angular momentum.
- Pause, play, speed up, slow down, and edit the universe while it runs.
- Generate simulation data for AI/ML models.
- Predict orbital stability and future trajectories.
- Compare exact physics against AI predictions.
- Load real astronomy data from trusted sources.
- Explain why an orbit is circular, elliptical, unstable, chaotic, or decaying.
- Eventually plan spacecraft transfers and maneuvers.

The guiding idea is simple: physics correctness first, interactivity second, AI third, polish and deployment fourth.

## 2. Problem Statement

Space physics is fascinating, but most learning tools split the experience into separate pieces:

- Textbooks explain equations but do not feel alive.
- Simulators show motion but often hide the underlying physics.
- Machine learning projects use datasets but rarely connect them to physical laws.
- Web demos are interactive but often simplify the science too much.

AstroRT solves this by building one continuous system where the same simulation can be studied, visualized, tested, optimized, used for data generation, connected to AI, and eventually deployed.

The project also solves a personal engineering problem: it creates a clear path from beginner-friendly Python experimentation to serious C++ performance engineering and modern web deployment.

## 3. Proposed Solution

AstroRT will be built in phases:

- Start with a Python research prototype to learn and validate the physics quickly.
- Rebuild the performance-critical simulation core in C++.
- Expose the C++ engine back to Python with pybind11.
- Use Python and PyTorch for AI/ML experiments.
- Build a web interface with React/Next.js and Three.js.
- Add a FastAPI backend for saved systems, simulation endpoints, and AI prediction endpoints.
- Package, benchmark, document, and deploy the project.

This hybrid architecture gives each language a job:

- Python helps us think, test, plot, and train models quickly.
- C++ helps us run the physics engine fast.
- JavaScript/TypeScript helps us build the interactive browser experience.

## 4. Target Users

AstroRT is designed for several audiences:

- Students learning orbital mechanics, numerical simulation, and AI.
- Developers who want a serious portfolio project involving physics, C++, Python, ML, and web engineering.
- Space enthusiasts who want to create and explore planetary systems.
- Educators who want visual explanations of gravity, orbits, stability, and chaos.
- Future researchers who want a sandbox for comparing exact physics, approximations, and learned surrogates.

The first target user is the builder: every phase should teach the concepts clearly while producing a real artifact.

## 5. Core Features

Each feature below includes what it is, why it matters, how it works, how to test it, and which future phase it supports.

### 5.1 N-Body Gravity

- What: A simulation where every body gravitationally attracts every other body.
- Why: This is the foundation of planetary motion, moon systems, asteroid clusters, and orbital instability.
- How: For each body, sum the acceleration caused by all other bodies using Newtonian gravity.
- Test: A two-body Sun-Earth system should produce a stable orbit with small energy drift.
- Future phase: Supports all later physics, C++ engine work, AI datasets, and web visualization.

### 5.2 Velocity-Verlet Integration

- What: A numerical method for stepping positions and velocities forward in time.
- Why: Orbital systems need long-term stability; naive integration can make planets spiral inward or fly away.
- How: Compute acceleration, update position, recompute acceleration, then update velocity using the average acceleration.
- Test: Compare relative energy drift over many orbits against a simple Euler method and verify Velocity-Verlet is more stable.
- Future phase: Becomes the first main integrator in both Python and C++.

### 5.3 Energy and Angular Momentum Tracking

- What: Runtime metrics that measure whether the simulation is preserving important physical quantities.
- Why: A pretty orbit is not enough; we need numerical evidence that the simulation is physically trustworthy.
- How: Compute total kinetic energy, gravitational potential energy, total energy, and angular momentum at each step or sample interval.
- Test: In a stable two-body orbit, relative drift should remain small over many orbits.
- Future phase: Supports validation, benchmarks, AI comparison, and research reports.

### 5.4 Real-Time Visualization

- What: A live view of bodies moving under gravity.
- Why: Visual feedback makes the physics easier to understand and debug.
- How: Phase 1 can use simple Python visualization; later phases use Three.js for browser-based 3D rendering.
- Test: Users should be able to see orbit trails, pause/play the simulation, and change time speed.
- Future phase: Evolves into the public web product.

### 5.5 Scenario Presets

- What: Saved starting systems such as Sun-Earth, inner Solar System, binary stars, or asteroid clusters.
- Why: Presets make testing and learning repeatable.
- How: Store body masses, positions, velocities, colors, and display settings in simple scenario definitions.
- Test: Loading the same preset twice should produce the same initial state and comparable metrics.
- Future phase: Supports web save/load, benchmarking, and dataset generation.

### 5.6 Dataset Generation

- What: Export simulated states and metrics for machine learning.
- Why: AI models need trustworthy data generated from a reliable physics engine.
- How: Save positions, velocities, masses, accelerations, labels, and stability metrics from many simulation runs.
- Test: Generated datasets should include consistent shapes, units, metadata, and reproducible seeds.
- Future phase: Enables stability classifiers, trajectory predictors, and learned force surrogates.

### 5.7 AI Stability Prediction

- What: A model that predicts whether a system is likely to remain stable.
- Why: Long simulations can be expensive; prediction can guide users and experiments.
- How: Train a PyTorch model on generated simulations labeled by drift, collision, ejection, or bounded behavior.
- Test: Evaluate on held-out scenarios and compare predictions against actual rollouts.
- Future phase: Becomes the first practical AI feature.

### 5.8 AI Trajectory Prediction

- What: A model that predicts future positions or approximate orbital evolution.
- Why: It teaches sequence modeling and lets users compare learned dynamics with physics-based simulation.
- How: Train on time-series windows of simulation states.
- Test: Compare predicted trajectories against exact simulation rollouts over short and medium horizons.
- Future phase: Supports educational comparison views and research extensions.

### 5.9 Barnes-Hut Approximation

- What: A tree-based approximation for computing far-away gravitational effects more efficiently.
- Why: Exact N-body gravity is O(N^2), which becomes slow as body count grows.
- How: Group distant bodies into cells and approximate their pull using center of mass when the cell is far enough.
- Test: Compare runtime and force error against exact pairwise gravity for increasing body counts.
- Future phase: Supports larger simulations and AI-assisted far-field approximation.

### 5.10 Spacecraft and Maneuvers

- What: Later support for spacecraft, thrust, burns, and transfer planning.
- Why: This expands the simulator from passive planets into mission design.
- How: Add controllable bodies with thrust vectors, fuel limits, and planned delta-v events.
- Test: Verify basic transfers and impulse changes against expected orbital behavior.
- Future phase: Supports mission-planning features after the core simulator is stable.

## 6. System Architecture

The final system has seven major layers:

### 6.1 Physics Engine

Responsible for bodies, units, gravity, integrators, collisions, metrics, and simulation stepping.

Phase 1 uses Python for clarity. Phase 2 moves the serious engine to C++.

### 6.2 Rendering Engine

Responsible for drawing bodies, trails, vectors, labels, and camera controls.

Phase 1 can use Python visualization. The final product uses Three.js for 3D browser rendering.

### 6.3 AI/ML Engine

Responsible for dataset loading, model training, prediction, evaluation, and explainability.

This layer uses PyTorch and should depend on trusted simulation data, not replace the physics engine too early.

### 6.4 Data Layer

Responsible for scenarios, generated datasets, saved user systems, benchmark outputs, and real astronomy imports.

Early data can be files. Later data may use a database and cloud storage.

### 6.5 Backend/API Layer

Responsible for serving simulations, saved systems, AI predictions, user data, and astronomy-data integration.

FastAPI is the planned backend framework.

### 6.6 Frontend/Product Layer

Responsible for the user-facing app: controls, dashboard, graph panels, scenario editor, and educational explanations.

React/Next.js and Three.js are the planned frontend stack.

### 6.7 Deployment Layer

Responsible for packaging, CI, Docker, hosting, monitoring, and reproducibility.

The likely deployment split is Vercel for frontend and Render, Fly.io, AWS, or a similar service for backend.

## 7. Technical Stack

### 7.1 Phase 1 Python Prototype

- Python
- NumPy
- Matplotlib or Pygame for early visualization
- pytest for tests
- Ruff/Black later for formatting and linting

Purpose: learn and validate the physics quickly.

### 7.2 Phase 2 C++ Physics Engine

- C++17 or C++20
- CMake
- Custom Vec2/Vec3 first, possible Eigen later
- GoogleTest or Catch2
- Optional OpenMP later

Purpose: build the high-performance engine.

### 7.3 Phase 3 Python Bindings

- pybind11
- CMake integration
- Python packaging support

Purpose: let Python call the fast C++ engine for experiments, plotting, and ML datasets.

### 7.4 Phase 4 AI/ML Layer

- Python
- PyTorch
- NumPy
- pandas
- Matplotlib
- Optional PyTorch Geometric for GNN experiments
- Optional MLflow or Weights & Biases for experiment tracking

Purpose: train models around trustworthy simulation data.

### 7.5 Phase 5 Web Platform

- TypeScript
- React
- Next.js
- Three.js
- Zustand or another lightweight state store if needed
- FastAPI backend

Purpose: make AstroRT interactive and usable by other people.

### 7.6 Phase 6 Research and Deployment

- Docker
- GitHub Actions
- Vercel for frontend
- Render, Fly.io, AWS, or similar for backend
- PostgreSQL if saved systems and users are added
- Benchmark reports and paper-style documentation

Purpose: make the project reproducible, deployable, and portfolio-ready.

## 8. Phase Roadmap

### Phase 0: Concept and Architecture

Define the project vision, phased architecture, learning goals, decision log, and first feature boundaries.

### Phase 1: Python Physics Prototype

Build a 2D N-body simulator with Newtonian gravity, Velocity-Verlet integration, energy tracking, angular momentum tracking, simple presets, simple visualization, sandbox editing, save/load, and data export.

Status: complete as of 2026-05-30. See `PHASE_1_REPORT.md`.

### Phase 2: Interactive Sandbox

Add user controls such as pause/play, time speed, reset, body creation, velocity dragging, zoom/pan, and scenario switching.

### Phase 3: C++ Physics Engine

Rebuild the stable physics core in C++ with tests and clean APIs.

### Phase 4: Python Bindings

Expose the C++ engine to Python through pybind11.

### Phase 5: AI/ML Layer

Generate datasets and train models for stability classification, short-horizon trajectory prediction, and possible force approximation.

### Phase 6: Web Platform

Build the browser app with React/Next.js, Three.js rendering, and FastAPI APIs.

### Phase 7: Real Astronomy Data

Import real solar-system and exoplanet data from trusted sources.

### Phase 8: Spacecraft and Mission Planning

Add spacecraft, thrust, delta-v events, and transfer-planning tools.

### Phase 9: Research-Grade Hybrid AI Physics Engine

Compare exact gravity, Barnes-Hut approximation, and AI-assisted surrogate models with rigorous benchmarks.

## 9. Phase 1 Python Prototype Plan

Phase 1 is about learning and validation, not final performance.

### 9.1 Goals

- Build a minimal but correct 2D N-body simulation.
- Learn how gravity becomes code.
- Learn why numerical integrators matter.
- Track energy and angular momentum.
- Visualize motion and orbit trails.
- Keep code simple enough to port to C++ later.

### 9.2 Planned Modules

- Body representation: mass, position, velocity, display radius, color.
- Force calculation: pairwise Newtonian acceleration.
- Integrator: Velocity-Verlet first, RK4 later as a reference option.
- Simulation loop: holds bodies, time step, current time, and stepping logic.
- Metrics: energy, angular momentum, drift.
- Scenarios: Sun-Earth, binary star, simple inner Solar System.
- Viewer: simple live 2D display.
- Browser lab: object inspector, camera tools, vector overlays, timeline, save/load, and export.
- Tests: physics sanity checks and conservation checks.

### 9.3 Acceptance Criteria

- A Sun-Earth style system orbits without obvious numerical collapse.
- Relative energy drift remains small over a chosen number of orbits.
- Angular momentum drift remains small in stable scenarios.
- The simulation can pause, reset, and switch presets.
- The browser lab can add/edit bodies, inspect realtime parameters, save/load systems, and export data.
- The code remains simple and educational.

## 10. Phase 2 C++ Engine Plan

Phase 2 turns the validated Python physics into a serious engine core.

### 10.1 Goals

- Rebuild the physics core in C++.
- Keep APIs clean and testable.
- Improve performance and memory control.
- Prepare for Python bindings and later web integration.

### 10.2 Planned Components

- Vec2/Vec3 math types.
- Body type.
- Simulation class.
- ForceModel interface.
- Integrator interface.
- Velocity-Verlet implementation.
- RK4 reference implementation.
- Metrics functions.
- Scenario loading.
- Unit tests.

### 10.3 Acceptance Criteria

- C++ tests reproduce key Phase 1 behavior.
- Energy drift is comparable to the Python implementation for the same scenario and time step.
- The engine can simulate many more bodies than the Python prototype at the same rough frame budget.

## 11. Phase 3 Python Bindings Plan

Phase 3 connects the C++ engine back to Python.

### 11.1 Goals

- Use pybind11 to expose C++ simulation classes and functions.
- Let Python run fast simulations without rewriting analysis code.
- Use C++ simulation output for plotting, data generation, and ML training.

### 11.2 Planned Interface

- Create simulations from Python.
- Add bodies from Python.
- Step simulations from Python.
- Read positions, velocities, masses, and metrics from Python.
- Export rollouts to NumPy-friendly formats.

### 11.3 Acceptance Criteria

- Python can import the compiled binding module.
- Python can create and step a C++ simulation.
- Results match the C++ tests and Phase 1 expectations.

## 12. Phase 4 AI/ML Plan

Phase 4 adds intelligence only after the physics data is trustworthy.

### 12.1 First AI Feature: Stability Classifier

- What: Predict whether a system is stable, colliding, ejecting, or highly chaotic.
- Why: It gives users fast insight without always waiting for long rollouts.
- How: Train a PyTorch model on generated simulations labeled by outcome.
- Test: Measure accuracy, precision/recall, and calibration on held-out systems.
- Future phase: Powers educational warnings and scenario analysis.

### 12.2 Second AI Feature: Trajectory Predictor

- What: Predict short-horizon future states.
- Why: It teaches sequence modeling and exposes the difference between learned prediction and physics simulation.
- How: Train on windows of positions, velocities, and masses.
- Test: Compare predicted positions against true rollout positions over increasing horizons.
- Future phase: Powers side-by-side physics vs AI comparison.

### 12.3 Research AI Feature: GNN Far-Field Surrogate

- What: Predict far-field gravitational effects using a graph neural network.
- Why: It may accelerate large simulations while preserving exact near-field physics.
- How: Train on residual acceleration: exact acceleration minus near-field acceleration.
- Test: Compare acceleration error, rollout drift, and runtime against exact and Barnes-Hut baselines.
- Future phase: Supports research-grade hybrid physics/AI simulation.

### 12.4 Research AI Feature: Hamiltonian Neural Networks

- What: Learn dynamics through an energy-like Hamiltonian structure.
- Why: Physical inductive bias can improve conservation behavior.
- How: Train models that learn a Hamiltonian and derive dynamics from it.
- Test: Compare long-term energy behavior against standard neural networks.
- Future phase: Supports paper-worthy experiments.

## 13. Phase 5 Web Platform Plan

Phase 5 turns AstroRT into a product people can use.

### 13.1 Frontend

- Build a React/Next.js app.
- Render bodies and trails with Three.js.
- Add controls for time, presets, camera, vectors, metrics, and body editing.
- Keep the first screen as the actual simulator, not a marketing page.

### 13.2 Backend

- Use FastAPI for simulation APIs, saved scenarios, AI prediction, and external data integration.
- Provide clean JSON contracts for systems, bodies, metrics, and predictions.
- Add authentication only after the core product is useful.

### 13.3 Acceptance Criteria

- A user can open the web app and run a preset simulation.
- A user can inspect energy and angular momentum metrics.
- A user can save and reload a custom scenario.
- A user can request an AI stability prediction when the ML layer exists.

## 14. Phase 6 Deployment Plan

Phase 6 makes AstroRT reproducible and shareable.

### 14.1 Packaging

- Add clear local setup instructions.
- Add one-command development workflows.
- Package Python and C++ pieces cleanly.
- Use Docker for backend deployment when useful.

### 14.2 CI and Quality

- Add GitHub Actions for tests and linting.
- Run Python tests, C++ tests, and frontend checks separately.
- Keep benchmark scripts reproducible.

### 14.3 Hosting

- Frontend: Vercel or similar.
- Backend: Render, Fly.io, AWS, or similar.
- Data: PostgreSQL when saved systems/users are needed.
- Artifacts: release notes, screenshots, demo GIFs, and benchmark reports.

## 15. Physics Concepts To Learn

- Vectors: position, velocity, acceleration, force.
- Newton's law of universal gravitation.
- Center of mass.
- Two-body orbital motion.
- Circular and elliptical orbits.
- Escape velocity.
- Conservation of energy.
- Conservation of angular momentum.
- Numerical integration.
- Euler integration and why it is unstable for orbits.
- Velocity-Verlet and symplectic behavior.
- Time step selection.
- N-body chaos and sensitivity to initial conditions.
- Collision handling and merging.
- Barnes-Hut tree approximation.
- Orbital transfers and delta-v later.

## 16. AI/ML Concepts To Learn

- Supervised learning.
- Train/validation/test splits.
- Feature engineering for physical systems.
- Normalization and units.
- Classification metrics.
- Regression metrics.
- Sequence prediction.
- Overfitting and generalization.
- PyTorch tensors, modules, losses, and optimizers.
- Graph neural networks.
- Physics-informed learning.
- Hamiltonian Neural Networks.
- Neural ODEs.
- Model evaluation against physics baselines.
- Why AI should assist the simulator rather than replace the validated physics core too early.

## 17. Testing and Validation Strategy

Testing must prove behavior, not just check that code runs.

### 17.1 Phase 1 Tests

- Two-body orbit sanity test.
- Energy drift test.
- Angular momentum drift test.
- Center-of-mass consistency test.
- Scenario loading test.
- Deterministic rollout test with a fixed seed.

### 17.2 Phase 2 C++ Tests

- Vec2/Vec3 math tests.
- Force calculation tests.
- Integrator tests.
- Python-vs-C++ comparison tests on the same simple scenario.
- Performance benchmarks for body counts.

### 17.3 AI Tests

- Dataset shape and metadata tests.
- No data leakage between train and test sets.
- Baseline model comparison.
- Held-out scenario evaluation.
- Rollout error evaluation.

### 17.4 Web Tests

- Scenario loading.
- UI controls.
- Metrics display.
- API contract tests.
- Visual sanity checks for rendering.

## 18. Dataset Generation Plan

Datasets should be generated only after the physics simulator is validated.

### 18.1 Dataset Contents

- Body masses.
- Positions.
- Velocities.
- Accelerations.
- Time step.
- Scenario metadata.
- Total energy.
- Angular momentum.
- Stability labels.
- Collision/ejection events.

### 18.2 Dataset Types

- Two-body clean orbit data.
- Three-body chaotic data.
- Multi-body random systems.
- Inner Solar System approximations.
- Binary star systems.
- Asteroid cluster systems.

### 18.3 Labels

- Stable.
- Collision.
- Ejection.
- High energy drift.
- Chaotic but bounded.

### 18.4 Validation

- Include units and metadata.
- Use reproducible random seeds.
- Split by scenario family so test data is meaningfully different from training data.

## 19. Research Extensions

Potential paper-worthy extensions:

- Exact N-body vs Barnes-Hut vs GNN surrogate comparison.
- Accuracy-latency Pareto plots.
- Energy and angular momentum drift comparisons across integrators.
- Hamiltonian Neural Networks for orbital dynamics.
- Learned stability classifiers for generated planetary systems.
- Real astronomy data replay and comparison.
- Hybrid engine where exact near-field physics is combined with learned far-field approximation.
- Web-based educational simulator with explainable physics diagnostics.

## 20. Portfolio Strategy

AstroRT should be presented as a staged engineering journey, not only a final demo.

### 20.1 GitHub

- Clear README with vision, screenshots, setup, and roadmap.
- Architecture diagram.
- Phase checklist.
- Benchmarks and plots.
- Reproducible examples.
- Clean issues or project board.

### 20.2 LinkedIn or Blog Posts

Possible posts:

- Why I started AstroRT.
- Turning Newtonian gravity into code.
- Why naive integrators break orbits.
- Velocity-Verlet explained visually.
- Python prototype to C++ engine.
- Using AI to predict orbital stability.
- Building a real-time space simulator in the browser.

### 20.3 Demo Materials

- GIF of orbit trails.
- Energy drift plot.
- Web demo link.
- Short architecture video.
- Paper-style report.

## 21. Sources and Reading List

### 21.1 Physics and Simulation

- Barnes-Hut original paper, "A hierarchical O(N log N) force-calculation algorithm": https://www.nature.com/articles/324446a0
- JPL Horizons solar-system ephemeris service: https://ssd.jpl.nasa.gov/horizons/

### 21.2 Astronomy Data

- NASA Exoplanet Archive API documentation: https://exoplanetarchive.ipac.caltech.edu/docs/program_interfaces.html
- NASA Open APIs: https://api.nasa.gov/

### 21.3 AI/ML

- PyTorch documentation: https://docs.pytorch.org/docs/stable/index.html
- Hamiltonian Neural Networks paper: https://papers.neurips.cc/paper/9672-hamiltonian-neural-networks

### 21.4 C++ and Python Integration

- pybind11 documentation: https://pybind11.readthedocs.io/en/stable/index.html

### 21.5 Web and Backend

- FastAPI documentation: https://fastapi.tiangolo.com/
- React documentation: https://react.dev/reference/react
- Next.js documentation: https://nextjs.org/docs
- Three.js documentation: https://threejs.org/docs/index.html

## 22. Decision Log

| Date | Decision | Reason | Status |
| --- | --- | --- | --- |
| 2026-05-28 | Use a Python-first prototype. | Python is best for learning, plotting, testing ideas, and generating early datasets quickly. | Locked |
| 2026-05-28 | Use C++ as the final performance physics core. | Real-time simulation benefits from C++ speed, memory control, and engine-style architecture. | Locked |
| 2026-05-28 | Use Velocity-Verlet as the first main integrator. | It is simple, stable for orbital systems, and a good first symplectic-style method to learn. | Locked |
| 2026-05-28 | Use PyTorch for AI/ML. | PyTorch is flexible, widely used, and strong for research-style model building. | Locked |
| 2026-05-28 | Use pybind11 for Python/C++ bindings. | It is a standard lightweight way to expose C++ classes and functions to Python. | Locked |
| 2026-05-28 | Use React/Next.js and Three.js for the web interface. | React/Next.js provides the app framework, while Three.js handles browser-based 3D rendering. | Locked |
| 2026-05-28 | Use FastAPI for backend APIs. | FastAPI is Python-friendly, fast to build with, and automatically provides OpenAPI documentation. | Locked |
| 2026-05-28 | Do not implement code until the master plan is created. | The project needs a single planning source before implementation begins. | Locked |
| 2026-05-28 | Start Phase 1 with a small pure-Python Vec2 type before NumPy-heavy data work. | The current environment has Python but no pip/NumPy, and a Vec2 type maps cleanly to the future C++ engine. | Locked |
| 2026-05-28 | Build Phase 1.1 as a standard-library browser visualizer before React/FastAPI. | This creates a local app immediately while preserving the later web architecture path. | Locked |
| 2026-05-28 | Add the first sandbox editor interaction as click-drag body creation. | It makes the simulator interactive while keeping Python as the authoritative physics engine. | Locked |
| 2026-05-29 | Add stationary body creation, wider mass/speed controls, and camera lock. | These controls make the browser sandbox easier to experiment with and inspect. | Locked |
| 2026-05-29 | Keep all preset and added bodies in one shared N-body gravity system. | New bodies should physically perturb existing bodies; visibility depends on mass scale. | Locked |
| 2026-05-29 | Add circular orbit initialization around selected bodies. | Users should be able to create orbiting bodies without manually guessing tangential velocity. | Locked |
| 2026-05-29 | Keep circular presets for validation and add elliptical presets for realism. | Circular orbits make drift easy to test; elliptical orbits better represent real planetary motion. | Locked |
| 2026-05-29 | Add visibly eccentric orbit tools and comet-style scenario. | Real Earth-like ellipses are subtle, so the sandbox needs exaggerated examples and an eccentricity control for learning. | Locked |
| 2026-05-29 | Add blank and cleaner lab scenarios. | Users need a no-preset workspace plus simpler starter systems for debugging orbit creation and interactions. | Locked |
| 2026-05-29 | Add observation tools: zoom, edge indicators, click focus, and focus isolation. | The simulator needs big-picture viewing and object inspection without changing physics. | Locked |
| 2026-05-29 | Add selected body editing for mass, velocity, radius, trail clearing, and removal. | The sandbox needs parameter correction after creation, and every physical edit should reset metric baselines. | Locked |
| 2026-05-30 | Close Phase 1 with save/load, data export, fit/reset view, clear-all-trails, and a Phase 1 report. | Phase 1 needs persistence, exportability, and a clean wrap-up before moving to the C++ engine. | Locked |
| 2026-05-30 | Add tabbed HUD, wheel zoom, manual pan, and velocity/acceleration overlays. | The Phase 1 tool should feel like a readable physics lab, not only a working backend demo. | Locked |
| 2026-05-30 | Expand the Phase 1 browser into a physics-lab interface with inspector presets, force/COM/closest overlays, timeline tools, and actual timestep reduction. | These features make Phase 1 useful for learning, debugging, and preparing datasets before the C++ rewrite. | Locked |
| 2026-05-31 | Add a browser close-encounter merge guardrail for point-mass fly-throughs. | Phase 1 point masses can pass unrealistically through the Sun and receive numerical slingshot energy; merging close pairs conserves mass and momentum for interactive experiments. | Locked |

## 23. Open Questions

- Should Phase 1 visualization start with Matplotlib for simplicity or Pygame for interactivity?
- Should Phase 1 use astronomical units, years, and solar masses, or SI units from the beginning?
- What should be the first benchmark scenario: Sun-Earth, binary stars, or a small inner Solar System?
- Should the C++ engine use a custom Vec3 type first or introduce Eigen early?
- In later phases, should collision handling support physical radii, fragmentation, accretion, or only mass/momentum-conserving merges?
- Should the first AI model classify stability or predict short-horizon trajectories?
- Should real astronomy data integration begin with JPL Horizons or NASA Exoplanet Archive?
- Should the first public demo be desktop Python, browser-only, or backend-powered web?
- What level of physical realism is required before adding spacecraft maneuvers?
- Should AstroRT eventually support WebAssembly for running the C++ engine directly in the browser?
