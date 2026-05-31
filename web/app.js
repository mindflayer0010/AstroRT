const canvas = document.querySelector("#space");
const ctx = canvas.getContext("2d");

// These DOM references are the bridge between UI controls and simulation data.
const hud = document.querySelector("#hud");
const hudDragHandle = document.querySelector("#hudDragHandle");
const collapseHudButton = document.querySelector("#collapseHud");
const hideHudButton = document.querySelector("#hideHud");
const showHudButton = document.querySelector("#showHud");
const tabButtons = [...document.querySelectorAll(".tab")];
const panels = [...document.querySelectorAll("[data-panel-tab]")];
const toggleButton = document.querySelector("#toggle");
const resetButton = document.querySelector("#reset");
const stepOnceButton = document.querySelector("#stepOnce");
const addModeButton = document.querySelector("#addMode");
const bodyPresetSelect = document.querySelector("#bodyPreset");
const scenarioSelect = document.querySelector("#scenario");
const presetGrid = document.querySelector("#presetGrid");
const speedInput = document.querySelector("#speed");
const speedValue = document.querySelector("#speedValue");
const newMassInput = document.querySelector("#newMass");
const massValue = document.querySelector("#massValue");
const stationaryInput = document.querySelector("#stationary");
const orbitVelocityInput = document.querySelector("#orbitVelocity");
const orbitEccentricityInput = document.querySelector("#orbitEccentricity");
const eccValue = document.querySelector("#eccValue");
const orbitRadiusText = document.querySelector("#orbitRadius");
const orbitCircularSpeedText = document.querySelector("#orbitCircularSpeed");
const orbitEscapeSpeedText = document.querySelector("#orbitEscapeSpeed");
const orbitPeriodText = document.querySelector("#orbitPeriod");
const orbitDragSpeedText = document.querySelector("#orbitDragSpeed");
const orbitSpeedErrorText = document.querySelector("#orbitSpeedError");
const edgeIndicatorsInput = document.querySelector("#edgeIndicators");
const orbitTargetSelect = document.querySelector("#orbitTarget");
const focusBodySelect = document.querySelector("#focusBody");
const zoomInput = document.querySelector("#zoom");
const zoomValue = document.querySelector("#zoomValue");
const focusModeSelect = document.querySelector("#focusMode");
const velocityVectorsInput = document.querySelector("#velocityVectors");
const accelerationVectorsInput = document.querySelector("#accelerationVectors");
const forceLinesInput = document.querySelector("#forceLines");
const selectedPullInput = document.querySelector("#selectedPull");
const centerOfMassMarkerInput = document.querySelector("#centerOfMassMarker");
const closestPairLineInput = document.querySelector("#closestPairLine");
const distanceUnitSelect = document.querySelector("#distanceUnit");
const massUnitSelect = document.querySelector("#massUnit");
const trackDistanceButton = document.querySelector("#trackDistance");
const clearMeasurementsButton = document.querySelector("#clearMeasurements");
const measurementHint = document.querySelector("#measurementHint");
const measurementList = document.querySelector("#measurementList");
const timeText = document.querySelector("#time");
const energyText = document.querySelector("#energy");
const angularText = document.querySelector("#angular");
const bodyCountText = document.querySelector("#bodyCount");
const scenarioHealthText = document.querySelector("#scenarioHealth");
const warningsBox = document.querySelector("#warnings");
const bodyReadout = document.querySelector("#bodyReadout");
const massHeader = document.querySelector("#massHeader");
const distanceHeader = document.querySelector("#distanceHeader");
const fitSystemButton = document.querySelector("#fitSystem");
const resetViewButton = document.querySelector("#resetView");
const clearAllTrailsButton = document.querySelector("#clearAllTrails");
const saveSystemButton = document.querySelector("#saveSystem");
const loadSystemButton = document.querySelector("#loadSystemButton");
const loadSystemFileInput = document.querySelector("#loadSystemFile");
const exportDataButton = document.querySelector("#exportData");
const selectedBodyName = document.querySelector("#selectedBodyName");
const selectedBodyHint = document.querySelector("#selectedBodyHint");
const editNameInput = document.querySelector("#editName");
const editColorInput = document.querySelector("#editColor");
const editMassInput = document.querySelector("#editMass");
const editRadiusInput = document.querySelector("#editRadius");
const editXInput = document.querySelector("#editX");
const editYInput = document.querySelector("#editY");
const editVxInput = document.querySelector("#editVx");
const editVyInput = document.querySelector("#editVy");
const applyBodyEditButton = document.querySelector("#applyBodyEdit");
const freezeBodyButton = document.querySelector("#freezeBody");
const cloneBodyButton = document.querySelector("#cloneBody");
const orbitSelectedButton = document.querySelector("#orbitSelected");
const clearTrailButton = document.querySelector("#clearTrail");
const removeBodyButton = document.querySelector("#removeBody");
const timelineInput = document.querySelector("#timeline");
const timelineValue = document.querySelector("#timelineValue");
const rewindFrameButton = document.querySelector("#rewindFrame");
const restoreFrameButton = document.querySelector("#restoreFrame");
const snapshotSystemButton = document.querySelector("#snapshotSystem");
const trySmallerStepButton = document.querySelector("#trySmallerStep");
const increaseStepButton = document.querySelector("#increaseStep");
const resetStepButton = document.querySelector("#resetStep");
const addGuide = document.querySelector("#addGuide");
const hoverCard = document.querySelector("#hoverCard");

let state = null;
let paused = false;
let addMode = false;
let dragStart = null;
let dragCurrent = null;
let panDrag = null;
let cameraOffset = [0, 0];
let suppressNextClick = false;
let stepAccumulator = 0;
let hudDrag = null;
let editorDirty = false;
let editorBodyName = null;
let stateHistory = [];
let timelineIndex = -1;
let viewingHistory = false;
let measurementMode = false;
let pendingMeasurementBody = null;
let trackedPairs = [];
let hoverBodyName = null;
let hoverPosition = [0, 0];

const AU_IN_KM = 149_597_870.7;
const SOLAR_MASS_IN_KG = 1.98847e30;
const EARTH_MASS_IN_SOLAR = 3.003e-6;
const JUPITER_MASS_IN_SOLAR = 9.545e-4;
const G = 4 * Math.PI * Math.PI;

const SCENARIO_LABELS = {
  blank: "Blank",
  single_sun: "Single Star",
  sun_earth: "Sun-Earth",
  sun_earth_elliptical: "Earth Ellipse",
  comet_sun: "Comet",
  binary_stars: "Binary Stars",
  sun_jupiter: "Sun-Jupiter",
  three_body_lab: "3-Body Lab",
  inner_solar_system: "Inner Solar",
  elliptical_inner_solar_system: "Inner Solar Ellipse",
};

const PRESET_CARDS = [
  ["blank", "Blank", "Build from nothing"],
  ["single_sun", "Star + planet", "Clean star workspace"],
  ["binary_stars", "Binary", "Two-star orbit"],
  ["comet_sun", "Star + comet", "High-eccentricity lab"],
  ["three_body_lab", "Three-body", "Chaotic close encounters"],
  ["inner_solar_system", "Inner solar", "Mercury through Mars"],
  ["custom", "Custom saved", "Load via Data tab"],
];

const BODY_PRESETS = {
  custom: {
    massExponent: -3,
    radius: null,
    color: [120, 230, 180],
    guide: "Custom body: adjust mass, then click-drag for manual velocity.",
  },
  asteroid: {
    massExponent: -10,
    radius: 3,
    color: [178, 180, 168],
    guide: "Asteroid: tiny mass. Use Orbit for stable test particles.",
  },
  earth: {
    massExponent: Math.log10(EARTH_MASS_IN_SOLAR),
    radius: 5,
    color: [90, 160, 255],
    guide: "Earth-like: best around a star. Enable Orbit, then click a position.",
  },
  jupiter: {
    massExponent: Math.log10(JUPITER_MASS_IN_SOLAR),
    radius: 7,
    color: [224, 178, 122],
    guide: "Jupiter-like: strong perturbations. Good for seeing gravity effects.",
  },
  star: {
    massExponent: 0,
    radius: 10,
    color: [255, 215, 95],
    guide: "Star: very massive. Use carefully; it can reshape the whole system.",
  },
};

function scenarioLabel(name) {
  if (state?.scenario === name && state.scenarioInfo?.label) {
    return state.scenarioInfo.label;
  }
  return SCENARIO_LABELS[name] || name.replaceAll("_", " ");
}

function setActiveTab(tabName) {
  // Tabs keep the HUD compact without changing any physics behavior.
  for (const button of tabButtons) {
    button.classList.toggle("active", button.dataset.tab === tabName);
  }
  for (const panel of panels) {
    panel.hidden = panel.dataset.panelTab !== tabName;
  }
}

function rgbToHex([r, g, b]) {
  return `#${[r, g, b].map((value) => Math.max(0, Math.min(255, Number(value))).toString(16).padStart(2, "0")).join("")}`;
}

function hexToRgb(hex) {
  const clean = hex.replace("#", "");
  return [
    Number.parseInt(clean.slice(0, 2), 16),
    Number.parseInt(clean.slice(2, 4), 16),
    Number.parseInt(clean.slice(4, 6), 16),
  ];
}

function healthLevel() {
  if (!state) {
    return "good";
  }
  if (state.energyDrift > 1.0e-2 || state.angularMomentumDrift > 1.0e-6) {
    return "bad";
  }
  if ((state.warnings || []).length > 0 || state.energyDrift > 1.0e-4) {
    return "warn";
  }
  return "good";
}

function rememberState() {
  if (!state || viewingHistory) {
    return;
  }

  const last = stateHistory[stateHistory.length - 1];
  if (last && last.time === state.time && last.bodies.length === state.bodies.length) {
    timelineIndex = stateHistory.length - 1;
    syncTimeline();
    return;
  }

  // Keep the whole current-run visual history from its start instead of a
  // rolling short buffer. This makes the timeline scrubber useful from T=0.
  stateHistory.push(structuredClone(state));
  timelineIndex = stateHistory.length - 1;
  syncTimeline();
}

function syncTimeline() {
  timelineInput.max = Math.max(0, stateHistory.length - 1);
  timelineInput.value = Math.max(0, timelineIndex);
  if (stateHistory.length === 0) {
    timelineValue.textContent = "live";
    return;
  }

  const firstTime = stateHistory[0]?.time || 0;
  timelineValue.textContent = viewingHistory
    ? `frame ${timelineIndex + 1}/${stateHistory.length} | t ${state.time.toFixed(3)} years`
    : `live | ${stateHistory.length} frames since t ${firstTime.toFixed(3)} years`;
}

function restartTimelineHistory() {
  // Reset/load starts a new timeline branch. The first recorded frame becomes
  // the beginning of that run, usually T=0 for scenario resets.
  stateHistory = [];
  timelineIndex = -1;
  viewingHistory = false;
  rememberState();
}

function resizeCanvas() {
  // Device-pixel-ratio handling keeps the canvas sharp on high-DPI screens.
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.floor(window.innerWidth * ratio);
  canvas.height = Math.floor(window.innerHeight * ratio);
  canvas.style.width = `${window.innerWidth}px`;
  canvas.style.height = `${window.innerHeight}px`;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
}

function color([r, g, b], alpha = 1) {
  // Python sends colors as [r, g, b]; canvas wants a CSS color string.
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function selectedMass() {
  // The slider is logarithmic: -6 means 10^-6 solar masses. A log slider gives
  // useful tiny/large ranges without making the UI awkward.
  return 10 ** Number(newMassInput.value);
}

function selectedBodyPreset() {
  return BODY_PRESETS[bodyPresetSelect.value] || BODY_PRESETS.custom;
}

function selectedBodyRadius() {
  const preset = selectedBodyPreset();
  if (preset.radius !== null) {
    return preset.radius;
  }
  return Math.max(3, Math.min(9, 3 + Math.log10(selectedMass() / 1.0e-8)));
}

function applyBodyPreset() {
  const preset = selectedBodyPreset();
  newMassInput.value = Math.max(
    Number(newMassInput.min),
    Math.min(Number(newMassInput.max), preset.massExponent),
  ).toFixed(2);
  updateHud();
}

function selectedStepRate() {
  // The speed slider is logarithmic. This gives us slow motion below 1
  // step/frame and fast-forward above 1 step/frame in one compact control.
  return 10 ** Number(speedInput.value);
}

function selectedEccentricity() {
  return Number(orbitEccentricityInput.value);
}

function selectedZoom() {
  // Log zoom keeps scale uniform while giving useful zoom-in and zoom-out range.
  return 10 ** Number(zoomInput.value);
}

function setZoomFromScale(scale) {
  // The slider stores log10(zoom), while camera math wants normal zoom.
  const min = Number(zoomInput.min);
  const max = Number(zoomInput.max);
  zoomInput.value = Math.max(min, Math.min(max, Math.log10(scale))).toFixed(2);
}

function setZoomAroundScreenPoint(nextZoom, screenX, screenY) {
  // Keep the world point under the cursor stable while zooming.
  const before = screenToWorld(screenX, screenY);
  const min = 10 ** Number(zoomInput.min);
  const max = 10 ** Number(zoomInput.max);
  setZoomFromScale(Math.max(min, Math.min(max, nextZoom)));
  const after = screenToWorld(screenX, screenY);
  cameraOffset[0] += before[0] - after[0];
  cameraOffset[1] += before[1] - after[1];
}

function worldScale() {
  return Math.min(window.innerWidth, window.innerHeight) * 0.22 * selectedZoom();
}

function cameraCenter() {
  // Locking changes the camera center, not the physics. The selected body can
  // keep moving while the canvas follows it.
  if (!state || focusBodySelect.value === "__free__") {
    return cameraOffset;
  }

  const focused = state.bodies.find((body) => body.name === focusBodySelect.value);
  if (!focused) {
    return cameraOffset;
  }
  return [focused.position[0] + cameraOffset[0], focused.position[1] + cameraOffset[1]];
}

function worldToScreen([x, y]) {
  // Physics uses AU around origin (0, 0). Canvas uses pixels from top-left.
  const scale = worldScale();
  const [cx, cy] = cameraCenter();
  return [window.innerWidth / 2 + (x - cx) * scale, window.innerHeight / 2 + (y - cy) * scale];
}

function screenToWorld(x, y) {
  // Inverse of worldToScreen. Mouse pixels become AU coordinates.
  const scale = worldScale();
  const [cx, cy] = cameraCenter();
  return [(x - window.innerWidth / 2) / scale + cx, (y - window.innerHeight / 2) / scale + cy];
}

function setAddMode(enabled) {
  // Add mode changes how canvas clicks behave. Keeping it in one helper avoids
  // the "I added a body but still cannot select it" trap.
  addMode = enabled;
  addModeButton.textContent = addMode ? "Adding..." : "Add body";
  canvas.classList.toggle("adding", addMode);
  updateAddGuide();
}

function setPaused(enabled) {
  // One helper keeps the button text and simulation state synchronized.
  paused = enabled;
  toggleButton.textContent = paused ? "Play" : "Pause";
}

function markEditorDirty() {
  // While these inputs are being edited, realtime state refreshes must not
  // overwrite typed values before the Apply button can read them.
  editorDirty = true;
  setPaused(true);
}

async function fetchState(steps) {
  // The backend advances the authoritative simulation. The browser only draws
  // the state it receives; it does not run physics itself yet.
  const response = await fetch(`/api/state?steps=${steps}`);
  state = await response.json();
  viewingHistory = false;
  syncScenarioOptions();
  syncFocusOptions();
  syncOrbitTargetOptions();
  updateHud();
  rememberState();
}

async function postJson(url, payload) {
  // Small helper for editor actions. The server returns the whole simulation
  // state after each edit so the UI and physics stay synchronized.
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const nextState = await response.json();
  if (nextState.error) {
    showMessage(nextState.error);
    return null;
  }
  state = nextState;
  viewingHistory = false;
  syncFocusOptions();
  syncOrbitTargetOptions();
  updateHud();
  draw();
  rememberState();
  return nextState;
}

async function getJson(url) {
  const response = await fetch(url);
  return response.json();
}

async function resetSimulation() {
  // Reset is server-side so metrics, trails, and body state all restart
  // together from the chosen scenario.
  const scenario = encodeURIComponent(scenarioSelect.value);
  const response = await fetch(`/api/reset?scenario=${scenario}`);
  state = await response.json();
  viewingHistory = false;
  trackedPairs = [];
  pendingMeasurementBody = null;
  syncFocusOptions();
  syncOrbitTargetOptions();
  updateHud();
  restartTimelineHistory();
}

async function addBody(start, end) {
  // In manual mode, the drag vector becomes initial velocity. In orbit mode,
  // Python computes circular orbital velocity around the selected target.
  const velocityScale = 5.0;
  const velocity = stationaryInput.checked
    ? [0, 0]
    : [(end[0] - start[0]) * velocityScale, (end[1] - start[1]) * velocityScale];
  const payload = {
    x: start[0],
    y: start[1],
    vx: velocity[0],
    vy: velocity[1],
    mass: selectedMass(),
    radius: selectedBodyRadius(),
    color: selectedBodyPreset().color,
  };

  if (orbitVelocityInput.checked && orbitTargetSelect.value) {
    payload.orbitTarget = orbitTargetSelect.value;
    payload.orbitEccentricity = selectedEccentricity();
  }

  const previousNames = new Set((state?.bodies || []).map((body) => body.name));
  const nextState = await postJson("/api/add_body", payload);
  if (!nextState) {
    return;
  }

  // Once the body exists, leave creation mode and select it immediately so the
  // user can edit mass/velocity without hunting for it.
  setAddMode(false);
  const addedBody =
    nextState.bodies.find((body) => !previousNames.has(body.name)) ||
    nextState.bodies[nextState.bodies.length - 1];
  if (addedBody) {
    focusBody(addedBody.name);
  }
}

function syncScenarioOptions() {
  // Scenarios come from Python so the UI stays in sync with server support.
  if (!state) {
    return;
  }

  if (scenarioSelect.options.length === 0) {
    for (const scenario of state.scenarios) {
      const option = document.createElement("option");
      option.value = scenario;
      option.textContent = scenarioLabel(scenario);
      scenarioSelect.append(option);
    }
  }

  if (![...scenarioSelect.options].some((option) => option.value === state.scenario)) {
    const option = document.createElement("option");
    option.value = state.scenario;
    option.textContent = state.scenario === "custom" ? "Custom" : state.scenario.replaceAll("_", " ");
    scenarioSelect.append(option);
  }
  scenarioSelect.value = state.scenario;
  renderPresetCards();
}

function renderPresetCards() {
  if (presetGrid.childElementCount > 0 || !state) {
    return;
  }

  for (const [scenario, label, description] of PRESET_CARDS) {
    const button = document.createElement("button");
    button.className = "preset-card";
    button.type = "button";
    button.disabled = scenario === "custom";
    button.dataset.scenario = scenario;

    const title = document.createElement("strong");
    title.textContent = label;
    const badge = document.createElement("span");
    badge.className = "stability-badge";
    badge.textContent = scenario === "custom" ? "saved" : (scenario === state.scenario ? state.scenarioInfo.stability : "preset");
    const copy = document.createElement("span");
    copy.textContent = description;

    button.append(title, badge, copy);
    button.addEventListener("click", async () => {
      scenarioSelect.value = scenario;
      await resetSimulation();
      setActiveTab("sim");
    });
    presetGrid.append(button);
  }
}

function syncFocusOptions() {
  // Body choices change when scenarios reset or user-added bodies appear.
  if (!state) {
    return;
  }

  const previous = focusBodySelect.value || "__free__";
  focusBodySelect.replaceChildren();

  const free = document.createElement("option");
  free.value = "__free__";
  free.textContent = "Free";
  focusBodySelect.append(free);

  for (const body of state.bodies) {
    const option = document.createElement("option");
    option.value = body.name;
    option.textContent = body.name;
    focusBodySelect.append(option);
  }

  const stillExists = previous === "__free__" || state.bodies.some((body) => body.name === previous);
  focusBodySelect.value = stillExists ? previous : "__free__";
}

function syncOrbitTargetOptions() {
  // Orbit targets mirror the current body list. A newly added body can become
  // the center for later orbit creation.
  if (!state) {
    return;
  }

  const previous = orbitTargetSelect.value;
  orbitTargetSelect.replaceChildren();

  if (state.bodies.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No target";
    orbitTargetSelect.append(option);
    orbitTargetSelect.value = "";
    return;
  }

  for (const body of state.bodies) {
    const option = document.createElement("option");
    option.value = body.name;
    option.textContent = body.name;
    orbitTargetSelect.append(option);
  }

  const stillExists = state.bodies.some((body) => body.name === previous);
  orbitTargetSelect.value = stillExists ? previous : state.bodies[0]?.name || "";
}

function updateHud() {
  // The HUD focuses on simulation health: time, energy drift, angular momentum.
  if (!state) {
    return;
  }

  timeText.textContent = `time: ${state.time.toFixed(3)} years`;
  energyText.textContent = `energy drift: ${state.energyDrift.toExponential(3)}`;
  angularText.textContent = `Lz drift: ${state.angularMomentumDrift.toExponential(3)}`;
  bodyCountText.textContent = `bodies: ${state.bodies.length}`;
  scenarioHealthText.textContent = `${state.scenarioInfo?.stability || "stable"} | dt ${Number(state.dt).toExponential(2)}`;
  scenarioHealthText.className = `health-badge ${healthLevel()}`;
  renderWarnings();
  const stepRate = selectedStepRate();
  speedValue.textContent =
    stepRate >= 1 ? `${stepRate.toFixed(1)} steps/frame` : `1 step/${Math.round(1 / stepRate)} frames`;
  massValue.textContent = `${selectedMass().toExponential(2)} solar masses`;
  eccValue.textContent = selectedEccentricity().toFixed(2);
  zoomValue.textContent = `${selectedZoom().toFixed(2)}x`;
  updateAddGuide();
  updateOrbitCalculator(dragStart, dragCurrent);
  renderBodyReadout();
  renderSelectedBodyEditor();
  renderMeasurementTools();
  refreshHoverCard();
  syncTimeline();
}

function updateAddGuide() {
  const preset = selectedBodyPreset();
  if (orbitVelocityInput.checked) {
    addGuide.textContent = `${preset.guide} Orbit mode: click where the body should start around ${orbitTargetSelect.value || "the target"}.`;
  } else if (stationaryInput.checked) {
    addGuide.textContent = `${preset.guide} Rest mode: click once to drop it with zero initial velocity.`;
  } else {
    addGuide.textContent = `${preset.guide} Manual mode: drag from position toward velocity direction.`;
  }
}

function updateOrbitCalculator(start = null, end = null) {
  const target = bodyByName(orbitTargetSelect.value);
  const orbitingMass = selectedMass();
  const position = start || selectedBody()?.position || null;

  if (!target || !position) {
    orbitRadiusText.textContent = "--";
    orbitCircularSpeedText.textContent = "--";
    orbitEscapeSpeedText.textContent = "--";
    orbitPeriodText.textContent = "--";
    orbitDragSpeedText.textContent = "--";
    orbitSpeedErrorText.textContent = "--";
    return;
  }

  const radius = Math.hypot(position[0] - target.position[0], position[1] - target.position[1]);
  const circular = circularOrbitSpeed(target.mass, orbitingMass, radius);
  const escape = escapeOrbitSpeed(target.mass, orbitingMass, radius);
  const periapsis = periapsisOrbitSpeed(target.mass, orbitingMass, radius, selectedEccentricity());
  const period = orbitPeriodYears(target.mass, orbitingMass, radius / Math.max(1.0 - selectedEccentricity(), 0.05));
  const dragSpeed = end ? Math.hypot(end[0] - position[0], end[1] - position[1]) * 5.0 : Number.NaN;
  const reference = orbitVelocityInput.checked ? periapsis : circular;
  const error = Number.isFinite(dragSpeed) && reference > 0 ? ((dragSpeed - reference) / reference) * 100 : Number.NaN;

  orbitRadiusText.textContent = formatDistance(radius);
  orbitCircularSpeedText.textContent = formatSpeed(circular);
  orbitEscapeSpeedText.textContent = formatSpeed(escape);
  orbitPeriodText.textContent = formatYears(period);
  orbitDragSpeedText.textContent = Number.isFinite(dragSpeed) ? formatSpeed(dragSpeed) : "--";
  orbitSpeedErrorText.textContent = Number.isFinite(error) ? `${error.toFixed(1)}%` : "--";
}

function renderWarnings() {
  const warnings = state?.warnings || [];
  warningsBox.hidden = warnings.length === 0;
  warningsBox.replaceChildren();
  for (const warning of warnings) {
    const item = document.createElement("div");
    item.textContent = warning;
    warningsBox.append(item);
  }
}

function showMessage(message) {
  // User-facing errors belong in the HUD, not only in the developer console.
  warningsBox.hidden = false;
  warningsBox.replaceChildren();
  const item = document.createElement("div");
  item.textContent = message;
  warningsBox.append(item);
}

function formatSci(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toExponential(2) : "--";
}

function formatSpeed(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `${number.toFixed(3)} AU/yr` : "--";
}

function formatYears(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `${number.toFixed(3)} yr` : "--";
}

function formatDistance(au) {
  const value = Number(au);
  if (!Number.isFinite(value)) {
    return "--";
  }

  if (distanceUnitSelect.value === "km") {
    return `${(value * AU_IN_KM).toExponential(3)} km`;
  }
  if (distanceUnitSelect.value === "million_km") {
    return `${(value * AU_IN_KM / 1.0e6).toExponential(3)} M km`;
  }
  return `${value.toExponential(3)} AU`;
}

function formatMass(solarMasses) {
  const value = Number(solarMasses);
  if (!Number.isFinite(value)) {
    return "--";
  }

  if (massUnitSelect.value === "kg") {
    return `${(value * SOLAR_MASS_IN_KG).toExponential(3)} kg`;
  }
  if (massUnitSelect.value === "earth") {
    return `${(value / EARTH_MASS_IN_SOLAR).toExponential(3)} Mearth`;
  }
  if (massUnitSelect.value === "jupiter") {
    return `${(value / JUPITER_MASS_IN_SOLAR).toExponential(3)} Mjup`;
  }
  return `${value.toExponential(3)} Msun`;
}

function distanceUnitLabel() {
  if (distanceUnitSelect.value === "km") {
    return "km";
  }
  if (distanceUnitSelect.value === "million_km") {
    return "M km";
  }
  return "AU";
}

function massUnitLabel() {
  if (massUnitSelect.value === "kg") {
    return "kg";
  }
  if (massUnitSelect.value === "earth") {
    return "Mearth";
  }
  if (massUnitSelect.value === "jupiter") {
    return "Mjup";
  }
  return "Msun";
}

function circularOrbitSpeed(centralMass, orbitingMass, radius) {
  if (radius <= 0) {
    return Number.NaN;
  }
  return Math.sqrt(G * (centralMass + orbitingMass) / radius);
}

function escapeOrbitSpeed(centralMass, orbitingMass, radius) {
  if (radius <= 0) {
    return Number.NaN;
  }
  return Math.sqrt(2 * G * (centralMass + orbitingMass) / radius);
}

function periapsisOrbitSpeed(centralMass, orbitingMass, radius, eccentricity) {
  if (radius <= 0) {
    return Number.NaN;
  }
  const boundedEccentricity = Math.max(0, Math.min(0.95, eccentricity));
  return Math.sqrt(G * (centralMass + orbitingMass) * (1 + boundedEccentricity) / radius);
}

function orbitPeriodYears(centralMass, orbitingMass, semiMajorAxis) {
  if (semiMajorAxis <= 0) {
    return Number.NaN;
  }
  return 2 * Math.PI * Math.sqrt((semiMajorAxis ** 3) / (G * (centralMass + orbitingMass)));
}

function renderBodyReadout() {
  // Per-body values come from Python's physics state. The table is intentionally
  // compact so it can update in realtime without overwhelming the canvas.
  bodyReadout.replaceChildren();
  massHeader.textContent = `m (${massUnitLabel()})`;
  distanceHeader.textContent = `r (${distanceUnitLabel()})`;
  for (const body of state.bodies) {
    const row = document.createElement("div");
    row.className = "body-row";
    if (body.name === focusBodySelect.value) {
      row.classList.add("selected");
    }
    row.title = "Click to lock camera and focus this body";
    row.addEventListener("click", () => focusBody(body.name));

    const name = document.createElement("span");
    name.className = "body-name";
    const swatch = document.createElement("span");
    swatch.className = "body-swatch";
    swatch.style.background = color(body.color, 1);
    name.append(swatch, document.createTextNode(body.name));

    const values = [
      formatMass(body.mass),
      formatDistance(body.distanceFromOrigin),
      formatSci(body.speed),
      formatSci(body.accelerationMagnitude),
      formatSci(body.kineticEnergy),
    ];

    row.append(name, ...values.map((value) => {
      const cell = document.createElement("span");
      cell.textContent = value;
      return cell;
    }));
    bodyReadout.append(row);
  }
}

function selectedBody() {
  if (!state || focusBodySelect.value === "__free__") {
    return null;
  }
  return state.bodies.find((body) => body.name === focusBodySelect.value) || null;
}

function bodyByName(name) {
  return state?.bodies.find((body) => body.name === name) || null;
}

function pairKey(a, b) {
  return [a, b].sort().join("::");
}

function distanceBetween(first, second) {
  return Math.hypot(
    first.position[0] - second.position[0],
    first.position[1] - second.position[1],
  );
}

function syncTrackedPairs() {
  if (!state) {
    trackedPairs = [];
    pendingMeasurementBody = null;
    return;
  }

  const names = new Set(state.bodies.map((body) => body.name));
  trackedPairs = trackedPairs.filter((pair) => names.has(pair.a) && names.has(pair.b));
  if (pendingMeasurementBody && !names.has(pendingMeasurementBody)) {
    pendingMeasurementBody = null;
  }
}

function setMeasurementMode(enabled) {
  measurementMode = enabled;
  pendingMeasurementBody = null;
  trackDistanceButton.textContent = measurementMode ? "Tracking..." : "Track pair";
  canvas.classList.toggle("measuring", measurementMode);
  renderMeasurementTools();
}

function clearTrackedMeasurements() {
  trackedPairs = [];
  pendingMeasurementBody = null;
  renderMeasurementTools();
  draw();
}

function renderHoverCard(body, clientX, clientY) {
  if (!body || addMode || dragStart) {
    hoverCard.hidden = true;
    hoverBodyName = null;
    return;
  }

  hoverBodyName = body.name;
  hoverPosition = [clientX, clientY];
  hoverCard.replaceChildren();

  const title = document.createElement("strong");
  title.textContent = body.name;
  hoverCard.append(title);

  const appendLine = (text) => {
    const line = document.createElement("span");
    line.textContent = text;
    hoverCard.append(line);
  };

  appendLine(`mass: ${formatMass(body.mass)}`);
  appendLine(`r: ${formatDistance(body.distanceFromOrigin)}`);

  const focused = selectedBody();
  if (focused && focused.name !== body.name) {
    appendLine(`d to ${focused.name}: ${formatDistance(distanceBetween(body, focused))}`);
  }
  appendLine(`speed: ${formatSci(body.speed)} AU/yr`);
  appendLine(`accel: ${formatSci(body.accelerationMagnitude)} AU/yr^2`);

  const margin = 14;
  hoverCard.hidden = false;
  const rect = hoverCard.getBoundingClientRect();
  const left = Math.min(window.innerWidth - rect.width - 8, clientX + margin);
  const top = Math.min(window.innerHeight - rect.height - 8, clientY + margin);
  hoverCard.style.left = `${Math.max(8, left)}px`;
  hoverCard.style.top = `${Math.max(8, top)}px`;
}

function refreshHoverCard() {
  if (!hoverBodyName || hoverCard.hidden) {
    return;
  }
  renderHoverCard(bodyByName(hoverBodyName), hoverPosition[0], hoverPosition[1]);
}

function handleMeasurementBodyClick(body) {
  if (!measurementMode || !body) {
    return false;
  }

  if (!pendingMeasurementBody) {
    pendingMeasurementBody = body.name;
    renderMeasurementTools();
    return true;
  }

  if (pendingMeasurementBody === body.name) {
    pendingMeasurementBody = null;
    renderMeasurementTools();
    return true;
  }

  const key = pairKey(pendingMeasurementBody, body.name);
  if (!trackedPairs.some((pair) => pair.key === key)) {
    trackedPairs.push({ key, a: pendingMeasurementBody, b: body.name });
  }
  pendingMeasurementBody = null;
  renderMeasurementTools();
  draw();
  return true;
}

function renderMeasurementTools() {
  syncTrackedPairs();
  measurementList.replaceChildren();

  if (measurementMode && pendingMeasurementBody) {
    measurementHint.textContent = `Now click the second body for ${pendingMeasurementBody}.`;
  } else if (measurementMode) {
    measurementHint.textContent = "Click the first body, then the second body.";
  } else {
    measurementHint.textContent = "Click Track pair, then click two bodies.";
  }

  for (const pair of trackedPairs) {
    const first = bodyByName(pair.a);
    const second = bodyByName(pair.b);
    if (!first || !second) {
      continue;
    }

    const row = document.createElement("div");
    row.className = "measurement-row";

    const value = document.createElement("span");
    value.textContent = `${pair.a} - ${pair.b}: ${formatDistance(distanceBetween(first, second))}`;

    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Remove";
    remove.addEventListener("click", () => {
      trackedPairs = trackedPairs.filter((tracked) => tracked.key !== pair.key);
      renderMeasurementTools();
      draw();
    });

    row.append(value, remove);
    measurementList.append(row);
  }
}

function setEditorDisabled(disabled) {
  for (const input of [editNameInput, editColorInput, editMassInput, editRadiusInput, editXInput, editYInput, editVxInput, editVyInput]) {
    input.disabled = disabled;
  }
  for (const button of [applyBodyEditButton, freezeBodyButton, cloneBodyButton, orbitSelectedButton, clearTrailButton, removeBodyButton]) {
    button.disabled = disabled;
  }
}

function renderSelectedBodyEditor() {
  // The editor works on the currently locked/focused body. It edits the real
  // Python simulation state, then resets drift baselines after physical edits.
  const body = selectedBody();
  if (!body) {
    editorDirty = false;
    editorBodyName = null;
    selectedBodyName.textContent = "No body selected";
    selectedBodyHint.textContent = "Click a body or row";
    editNameInput.value = "";
    editColorInput.value = "#ffffff";
    editMassInput.value = "";
    editRadiusInput.value = "";
    editXInput.value = "";
    editYInput.value = "";
    editVxInput.value = "";
    editVyInput.value = "";
    setEditorDisabled(true);
    return;
  }

  if (editorBodyName !== body.name) {
    editorDirty = false;
    editorBodyName = body.name;
  }

  selectedBodyName.textContent = body.name;
  selectedBodyHint.textContent = editorDirty
    ? "paused for editing"
    : `r ${formatDistance(body.distanceFromOrigin)} | v ${formatSci(body.speed)} AU/yr`;
  setEditorDisabled(false);

  if (editorDirty) {
    return;
  }

  if (document.activeElement !== editNameInput) {
    editNameInput.value = body.name;
  }
  if (document.activeElement !== editColorInput) {
    editColorInput.value = rgbToHex(body.color);
  }
  if (document.activeElement !== editMassInput) {
    editMassInput.value = body.mass.toPrecision(8);
  }
  if (document.activeElement !== editRadiusInput) {
    editRadiusInput.value = body.radius.toPrecision(4);
  }
  if (document.activeElement !== editXInput) {
    editXInput.value = body.position[0].toPrecision(8);
  }
  if (document.activeElement !== editYInput) {
    editYInput.value = body.position[1].toPrecision(8);
  }
  if (document.activeElement !== editVxInput) {
    editVxInput.value = body.velocity[0].toPrecision(8);
  }
  if (document.activeElement !== editVyInput) {
    editVyInput.value = body.velocity[1].toPrecision(8);
  }
}

function systemRadius() {
  // Returns the largest distance from the camera origin needed to see bodies
  // and recent trails. It is display-only; physics coordinates stay unchanged.
  if (!state || state.bodies.length === 0) {
    return 1;
  }

  let maxRadius = 0;
  for (const body of state.bodies) {
    const points = [body.position, ...(body.trail || [])];
    for (const [x, y] of points) {
      maxRadius = Math.max(maxRadius, Math.hypot(x, y));
    }
  }
  return Math.max(maxRadius, 0.25);
}

function fitSystemView() {
  // Fit works by returning to free camera and choosing a zoom that keeps the
  // full system inside the shortest screen dimension.
  focusBodySelect.value = "__free__";
  focusModeSelect.value = "off";
  cameraOffset = [0, 0];
  setZoomFromScale(1.75 / systemRadius());
  updateHud();
  draw();
}

function resetView() {
  focusBodySelect.value = "__free__";
  focusModeSelect.value = "off";
  cameraOffset = [0, 0];
  zoomInput.value = "0";
  updateHud();
  draw();
}

function downloadJson(filename, payload) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function saveSystem() {
  const payload = await getJson("/api/export_system");
  downloadJson(`astro_rt_system_${Date.now()}.json`, payload);
}

async function snapshotSystem() {
  const payload = await getJson("/api/export_system");
  payload.snapshotTime = state?.time || 0;
  downloadJson(`astro_rt_snapshot_${Date.now()}.json`, payload);
}

function systemPayloadFromState(sourceState) {
  return {
    format: "astro_rt_system",
    version: 1,
    scenario: sourceState.scenario || "custom",
    time: sourceState.time,
    dt: sourceState.dt,
    softening: sourceState.softening,
    collisionDistance: sourceState.collisionDistance,
    bodies: sourceState.bodies.map((body) => ({
      name: body.name,
      mass: body.mass,
      position: body.position,
      velocity: body.velocity,
      radius: body.radius,
      color: body.color,
    })),
  };
}

async function restoreTimelineFrame() {
  if (!viewingHistory || !state) {
    showMessage("Scrub the timeline to a saved frame before restoring.");
    return;
  }

  const restored = await postJson("/api/load_system", systemPayloadFromState(state));
  if (restored) {
    restartTimelineHistory();
    showMessage(`Restored live simulation to t=${restored.time.toFixed(3)} years.`);
  }
}

async function exportData() {
  const payload = await getJson("/api/export_data");
  downloadJson(`astro_rt_phase1_data_${Date.now()}.json`, payload);
}

async function loadSystemFromFile(file) {
  try {
    const payload = JSON.parse(await file.text());
    editorDirty = false;
    const nextState = await postJson("/api/load_system", payload);
    if (nextState) {
      trackedPairs = [];
      pendingMeasurementBody = null;
      restartTimelineHistory();
      resetView();
    }
  } catch (error) {
    showMessage(`Could not load system: ${error.message}`);
  }
}

async function clearAllTrails() {
  await postJson("/api/clear_all_trails", {});
}

function focusBody(name) {
  focusBodySelect.value = name;
  // Selecting a body should not silently change visibility mode. Focus mode
  // stays Off/Dim/Solo exactly as the user chose it.
  zoomInput.value = Math.max(Number(zoomInput.value), 0.45).toFixed(2);
  updateHud();
  draw();
}

async function applySelectedBodyEdit() {
  const body = selectedBody();
  if (!body) {
    return;
  }

  const mass = Number(editMassInput.value);
  const radius = Number(editRadiusInput.value);
  const x = Number(editXInput.value);
  const y = Number(editYInput.value);
  const vx = Number(editVxInput.value);
  const vy = Number(editVyInput.value);
  if (![mass, radius, x, y, vx, vy].every(Number.isFinite) || mass <= 0 || radius <= 0) {
    selectedBodyHint.textContent = "enter finite mass/radius/position/velocity values";
    return;
  }

  editorDirty = false;
  await postJson("/api/update_body", {
    name: body.name,
    newName: editNameInput.value,
    mass,
    radius,
    color: hexToRgb(editColorInput.value),
    x,
    y,
    vx,
    vy,
  });
}

async function freezeSelectedBody() {
  const body = selectedBody();
  if (!body) {
    return;
  }
  editorDirty = false;
  await postJson("/api/freeze_body", { name: body.name });
}

async function cloneSelectedBody() {
  const body = selectedBody();
  if (!body) {
    return;
  }
  editorDirty = false;
  const nextState = await postJson("/api/clone_body", { name: body.name });
  const copy = nextState?.bodies[nextState.bodies.length - 1];
  if (copy) {
    focusBody(copy.name);
  }
}

function orbitAroundSelectedBody() {
  const body = selectedBody();
  if (!body) {
    return;
  }
  orbitVelocityInput.checked = true;
  stationaryInput.checked = false;
  orbitTargetSelect.value = body.name;
  setActiveTab("add");
  setAddMode(true);
}

async function stepOnce() {
  setPaused(true);
  await fetchState(1);
  draw();
}

async function halveTimestep() {
  // This changes the real integrator timestep, unlike playback speed. Smaller
  // dt can reduce numerical drift around close encounters or fast periapsis
  // motion, but it also makes simulated years advance more slowly.
  if (!state) {
    return;
  }
  const nextDt = Math.max(1.0e-8, Number(state.dt) * 0.5);
  await postJson("/api/set_dt", { dt: nextDt });
}

async function doubleTimestep() {
  // This is the "undo-ish" partner to Halve dt. It makes each physics step
  // cover more simulated time again. That is faster, but can be less accurate.
  if (!state) {
    return;
  }
  const defaultDt = Number(state.defaultDt || state.dt);
  const nextDt = Math.min(defaultDt * 16, Number(state.dt) * 2);
  await postJson("/api/set_dt", { dt: nextDt });
}

async function resetTimestep() {
  // Restore the scenario's recommended browser timestep after experimenting.
  await postJson("/api/reset_dt", {});
}

function rewindFrame() {
  if (stateHistory.length === 0) {
    return;
  }
  setPaused(true);
  timelineIndex = Math.max(0, timelineIndex - 1);
  state = structuredClone(stateHistory[timelineIndex]);
  viewingHistory = true;
  updateHud();
  draw();
}

async function clearSelectedTrail() {
  const body = selectedBody();
  if (!body) {
    return;
  }
  await postJson("/api/clear_body_trail", { name: body.name });
}

async function removeSelectedBody() {
  const body = selectedBody();
  if (!body) {
    return;
  }

  const removedName = body.name;
  await postJson("/api/remove_body", { name: removedName });
  if (focusBodySelect.value === removedName) {
    focusBodySelect.value = "__free__";
  }
  updateHud();
  draw();
}

function shouldDrawBody(body) {
  return focusModeSelect.value !== "solo" || focusBodySelect.value === "__free__" || body.name === focusBodySelect.value;
}

function bodyAlpha(body) {
  if (focusModeSelect.value !== "dim" || focusBodySelect.value === "__free__" || body.name === focusBodySelect.value) {
    return 1;
  }
  return 0.18;
}

function drawVector(body, vector, scale, strokeStyle, label) {
  const magnitude = Math.hypot(vector[0], vector[1]);
  if (!Number.isFinite(magnitude) || magnitude === 0) {
    return;
  }

  const alpha = bodyAlpha(body);
  const [x, y] = worldToScreen(body.position);
  const length = Math.min(90, Math.max(14, magnitude * scale));
  const ux = vector[0] / magnitude;
  const uy = vector[1] / magnitude;
  const endX = x + ux * length;
  const endY = y + uy * length;
  const angle = Math.atan2(uy, ux);
  const arrowColor = strokeStyle.replace("ALPHA", `${0.82 * alpha}`);

  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(endX, endY);
  ctx.strokeStyle = arrowColor;
  ctx.lineWidth = 1.4;
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(endX, endY);
  ctx.lineTo(endX - Math.cos(angle - 0.45) * 8, endY - Math.sin(angle - 0.45) * 8);
  ctx.lineTo(endX - Math.cos(angle + 0.45) * 8, endY - Math.sin(angle + 0.45) * 8);
  ctx.closePath();
  ctx.fillStyle = arrowColor;
  ctx.fill();

  ctx.fillStyle = `rgba(238, 243, 255, ${0.72 * alpha})`;
  ctx.font = "10px Cascadia Mono, Consolas, monospace";
  ctx.fillText(label, endX + 4, endY - 4);
}

function drawVectors() {
  if (!state) {
    return;
  }

  for (const body of state.bodies) {
    if (!shouldDrawBody(body)) {
      continue;
    }
    if (velocityVectorsInput.checked) {
      drawVector(body, body.velocity, 9, "rgba(95, 210, 255, ALPHA)", "v");
    }
    if (accelerationVectorsInput.checked) {
      drawVector(body, body.acceleration, 1200, "rgba(255, 205, 96, ALPHA)", "a");
    }
  }
}

function drawForceLines() {
  if (!state || !forceLinesInput.checked) {
    return;
  }

  const maxForce = Math.max(
    ...state.bodies.map((body) => body.mass * Math.hypot(body.acceleration[0], body.acceleration[1])),
    0,
  );
  if (maxForce === 0) {
    return;
  }

  for (const body of state.bodies) {
    if (!shouldDrawBody(body)) {
      continue;
    }
    const [x, y] = worldToScreen(body.position);
    const [ax, ay] = body.acceleration;
    const magnitude = Math.hypot(ax, ay);
    if (magnitude === 0) {
      continue;
    }

    // F = m*a. The arrow direction is the acceleration direction, while length
    // is scaled by relative net force so tiny and huge bodies remain readable.
    const forceMagnitude = body.mass * magnitude;
    const relativeLength = Math.sqrt(forceMagnitude / maxForce);
    const length = 24 + relativeLength * 82;
    const ux = ax / magnitude;
    const uy = ay / magnitude;
    const endX = x + ux * length;
    const endY = y + uy * length;
    const angle = Math.atan2(uy, ux);
    const alpha = bodyAlpha(body);

    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = `rgba(255, 136, 92, ${0.78 * alpha})`;
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(endX - Math.cos(angle - 0.46) * 9, endY - Math.sin(angle - 0.46) * 9);
    ctx.lineTo(endX - Math.cos(angle + 0.46) * 9, endY - Math.sin(angle + 0.46) * 9);
    ctx.closePath();
    ctx.fillStyle = `rgba(255, 136, 92, ${0.86 * alpha})`;
    ctx.fill();

    if (alpha > 0.3) {
      ctx.fillStyle = `rgba(255, 205, 184, ${0.82 * alpha})`;
      ctx.font = "10px Cascadia Mono, Consolas, monospace";
      ctx.fillText(`F ${forceMagnitude.toExponential(1)}`, endX + 5, endY + 11);
    }
  }
}

function accelerationDueToBody(body, attractor) {
  // This is one pairwise contribution, not the net acceleration. It answers:
  // "How much is `attractor` alone pulling on `body` right now?"
  const dx = attractor.position[0] - body.position[0];
  const dy = attractor.position[1] - body.position[1];
  const distanceSq = dx * dx + dy * dy;
  if (distanceSq === 0) {
    return [0, 0];
  }
  const distance = Math.sqrt(distanceSq);
  const scale = G * attractor.mass / (distanceSq * distance);
  return [dx * scale, dy * scale];
}

function drawSelectedPullLines() {
  if (!state || !selectedPullInput.checked || focusBodySelect.value === "__free__") {
    return;
  }

  const attractor = bodyByName(focusBodySelect.value);
  if (!attractor) {
    return;
  }

  const contributions = state.bodies
    .filter((body) => body.name !== attractor.name && shouldDrawBody(body))
    .map((body) => {
      const acceleration = accelerationDueToBody(body, attractor);
      const accelerationMagnitude = Math.hypot(acceleration[0], acceleration[1]);
      return {
        body,
        acceleration,
        accelerationMagnitude,
        forceMagnitude: body.mass * accelerationMagnitude,
      };
    })
    .filter((entry) => entry.accelerationMagnitude > 0);

  const maxForce = Math.max(...contributions.map((entry) => entry.forceMagnitude), 0);
  if (maxForce === 0) {
    return;
  }

  for (const entry of contributions) {
    const { body, acceleration, accelerationMagnitude, forceMagnitude } = entry;
    const [x, y] = worldToScreen(body.position);
    const [targetX, targetY] = worldToScreen(attractor.position);
    const alpha = bodyAlpha(body);
    const ux = acceleration[0] / accelerationMagnitude;
    const uy = acceleration[1] / accelerationMagnitude;
    const relativeLength = Math.sqrt(forceMagnitude / maxForce);
    const length = 20 + relativeLength * 68;
    const endX = x + ux * length;
    const endY = y + uy * length;
    const angle = Math.atan2(uy, ux);

    // Faint connector shows the body that is causing this one contribution.
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(targetX, targetY);
    ctx.setLineDash([3, 7]);
    ctx.strokeStyle = `rgba(181, 134, 255, ${0.22 * alpha})`;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.setLineDash([]);

    // Bright arrow starts at the affected body and points toward the selected
    // attractor. This makes a small perturbing body visible even when the net
    // force arrow still points mostly toward the Sun.
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = `rgba(190, 150, 255, ${0.88 * alpha})`;
    ctx.lineWidth = 1.7;
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(endX - Math.cos(angle - 0.46) * 8, endY - Math.sin(angle - 0.46) * 8);
    ctx.lineTo(endX - Math.cos(angle + 0.46) * 8, endY - Math.sin(angle + 0.46) * 8);
    ctx.closePath();
    ctx.fillStyle = `rgba(190, 150, 255, ${0.94 * alpha})`;
    ctx.fill();
  }
}

function drawCenterOfMass() {
  if (!state || !centerOfMassMarkerInput.checked) {
    return;
  }

  const [x, y] = worldToScreen(state.diagnostics.centerOfMass);
  ctx.beginPath();
  ctx.arc(x, y, 6, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(255, 255, 255, 0.78)";
  ctx.lineWidth = 1.4;
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x - 9, y);
  ctx.lineTo(x + 9, y);
  ctx.moveTo(x, y - 9);
  ctx.lineTo(x, y + 9);
  ctx.stroke();
  ctx.fillStyle = "rgba(238, 243, 255, 0.82)";
  ctx.font = "10px Cascadia Mono, Consolas, monospace";
  ctx.fillText("COM", x + 8, y - 8);
}

function drawClosestPair() {
  if (!state || !closestPairLineInput.checked) {
    return;
  }

  const pair = state.diagnostics.closestPair;
  if (!pair.a || !pair.b) {
    return;
  }
  const first = state.bodies.find((body) => body.name === pair.a);
  const second = state.bodies.find((body) => body.name === pair.b);
  if (!first || !second || !shouldDrawBody(first) || !shouldDrawBody(second)) {
    return;
  }

  const a = worldToScreen(first.position);
  const b = worldToScreen(second.position);
  ctx.beginPath();
  ctx.moveTo(a[0], a[1]);
  ctx.lineTo(b[0], b[1]);
  ctx.strokeStyle = "rgba(255, 120, 120, 0.52)";
  ctx.setLineDash([4, 5]);
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "rgba(255, 190, 190, 0.84)";
  ctx.font = "10px Cascadia Mono, Consolas, monospace";
  ctx.fillText(`closest ${formatDistance(pair.distance)}`, (a[0] + b[0]) / 2 + 6, (a[1] + b[1]) / 2 - 6);
}

function drawTrackedMeasurements() {
  if (!state || trackedPairs.length === 0) {
    return;
  }

  for (const pair of trackedPairs) {
    const first = bodyByName(pair.a);
    const second = bodyByName(pair.b);
    if (!first || !second || !shouldDrawBody(first) || !shouldDrawBody(second)) {
      continue;
    }

    const a = worldToScreen(first.position);
    const b = worldToScreen(second.position);
    const distance = distanceBetween(first, second);

    ctx.beginPath();
    ctx.moveTo(a[0], a[1]);
    ctx.lineTo(b[0], b[1]);
    ctx.strokeStyle = "rgba(96, 235, 190, 0.68)";
    ctx.setLineDash([7, 4]);
    ctx.lineWidth = 1.4;
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = "rgba(180, 255, 230, 0.92)";
    ctx.font = "11px Cascadia Mono, Consolas, monospace";
    ctx.fillText(formatDistance(distance), (a[0] + b[0]) / 2 + 7, (a[1] + b[1]) / 2 + 13);
  }
}

function drawBackground() {
  // Draw a lightweight star field directly on canvas. This is visual only; it
  // has no relationship to simulated bodies.
  ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
  ctx.fillStyle = "#05070d";
  ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

  ctx.fillStyle = "rgba(255, 255, 255, 0.38)";
  for (let i = 0; i < 90; i += 1) {
    const x = (i * 137.5) % window.innerWidth;
    const y = (i * 83.1) % window.innerHeight;
    ctx.fillRect(x, y, 1, 1);
  }
}

function drawBody(body) {
  if (!shouldDrawBody(body)) {
    return;
  }

  const alpha = bodyAlpha(body);
  // Trails show the path history, making orbital shape easier to read.
  if (body.trail.length > 1) {
    ctx.beginPath();
    for (let i = 0; i < body.trail.length; i += 1) {
      const [x, y] = worldToScreen(body.trail[i]);
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.strokeStyle = color(body.color, 0.55 * alpha);
    ctx.lineWidth = 1.2;
    ctx.stroke();
  }

  const [x, y] = worldToScreen(body.position);
  ctx.beginPath();
  ctx.arc(x, y, body.radius, 0, Math.PI * 2);
  ctx.fillStyle = color(body.color, alpha);
  ctx.shadowColor = color(body.color, 0.7 * alpha);
  ctx.shadowBlur = Math.max(8, body.radius * 2);
  ctx.fill();
  ctx.shadowBlur = 0;

  ctx.fillStyle = `rgba(238, 243, 255, ${0.82 * alpha})`;
  ctx.font = "12px Cascadia Mono, Consolas, monospace";
  if (alpha > 0.3) {
    ctx.fillText(body.name, x + body.radius + 6, y - body.radius - 4);
  }
}

function drawEdgeIndicators() {
  if (!state || !edgeIndicatorsInput.checked) {
    return;
  }

  const pad = 24;
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  for (const body of state.bodies) {
    if (!shouldDrawBody(body)) {
      continue;
    }

    const [x, y] = worldToScreen(body.position);
    const outside = x < pad || x > window.innerWidth - pad || y < pad || y > window.innerHeight - pad;
    if (!outside) {
      continue;
    }

    const dx = x - cx;
    const dy = y - cy;
    const length = Math.hypot(dx, dy) || 1;
    const ux = dx / length;
    const uy = dy / length;
    const edgeX = Math.max(pad, Math.min(window.innerWidth - pad, cx + ux * Math.min(window.innerWidth / 2 - pad, Math.abs(dx))));
    const edgeY = Math.max(pad, Math.min(window.innerHeight - pad, cy + uy * Math.min(window.innerHeight / 2 - pad, Math.abs(dy))));
    const angle = Math.atan2(uy, ux);
    const alpha = bodyAlpha(body);

    ctx.save();
    ctx.translate(edgeX, edgeY);
    ctx.rotate(angle);
    ctx.beginPath();
    ctx.moveTo(12, 0);
    ctx.lineTo(-8, -7);
    ctx.lineTo(-8, 7);
    ctx.closePath();
    ctx.fillStyle = color(body.color, 0.9 * alpha);
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = `rgba(238, 243, 255, ${0.78 * alpha})`;
    ctx.font = "11px Cascadia Mono, Consolas, monospace";
    ctx.fillText(body.name, edgeX + 8, edgeY - 8);
  }
}

function findBodyAtScreen(x, y) {
  if (!state) {
    return null;
  }

  for (let index = state.bodies.length - 1; index >= 0; index -= 1) {
    const body = state.bodies[index];
    const [sx, sy] = worldToScreen(body.position);
    const hitRadius = Math.max(12, body.radius + 6);
    if (Math.hypot(x - sx, y - sy) <= hitRadius) {
      return body;
    }
  }
  return null;
}

function drawDragPreview() {
  if (!dragStart || !dragCurrent) {
    return;
  }

  const start = worldToScreen(dragStart);
  const end = worldToScreen(dragCurrent);
  ctx.beginPath();
  ctx.moveTo(start[0], start[1]);
  ctx.lineTo(end[0], end[1]);
  ctx.strokeStyle = "rgba(120, 230, 180, 0.9)";
  ctx.lineWidth = 2;
  ctx.stroke();

  // Arrowhead: the drag vector is the initial velocity direction.
  const angle = Math.atan2(end[1] - start[1], end[0] - start[0]);
  const arrowSize = 11;
  ctx.beginPath();
  ctx.moveTo(end[0], end[1]);
  ctx.lineTo(end[0] - Math.cos(angle - 0.45) * arrowSize, end[1] - Math.sin(angle - 0.45) * arrowSize);
  ctx.lineTo(end[0] - Math.cos(angle + 0.45) * arrowSize, end[1] - Math.sin(angle + 0.45) * arrowSize);
  ctx.closePath();
  ctx.fillStyle = "rgba(120, 230, 180, 0.95)";
  ctx.fill();

  ctx.beginPath();
  ctx.arc(start[0], start[1], 5, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(120, 230, 180, 1)";
  ctx.fill();

  const manualSpeed = Math.hypot(dragCurrent[0] - dragStart[0], dragCurrent[1] - dragStart[1]) * 5.0;
  const speed = stationaryInput.checked ? 0 : manualSpeed;
  const target = bodyByName(orbitTargetSelect.value);
  const radius = target ? Math.hypot(dragStart[0] - target.position[0], dragStart[1] - target.position[1]) : Number.NaN;
  const requiredSpeed = target
    ? periapsisOrbitSpeed(target.mass, selectedMass(), radius, orbitVelocityInput.checked ? selectedEccentricity() : 0)
    : Number.NaN;
  const speedError = Number.isFinite(requiredSpeed) && requiredSpeed > 0
    ? ((speed - requiredSpeed) / requiredSpeed) * 100
    : Number.NaN;
  const mode = orbitVelocityInput.checked
    ? `orbit ${orbitTargetSelect.value || "target"} e=${selectedEccentricity().toFixed(2)}`
    : `v ${speed.toFixed(2)} AU/yr`;
  const errorLabel = Number.isFinite(speedError) ? ` | err ${speedError.toFixed(0)}%` : "";
  const label = `${mode} | need ${formatSpeed(requiredSpeed)}${errorLabel}`;
  ctx.font = "13px Cascadia Mono, Consolas, monospace";
  ctx.fillStyle = "rgba(238, 243, 255, 0.92)";
  ctx.fillText(label, end[0] + 12, end[1] - 12);

  updateOrbitCalculator(dragStart, dragCurrent);
}

function draw() {
  // Rendering is rebuilt from the latest state every frame.
  drawBackground();
  if (state) {
    for (const body of state.bodies) {
      drawBody(body);
    }
  }
  drawForceLines();
  drawSelectedPullLines();
  drawVectors();
  drawCenterOfMass();
  drawClosestPair();
  drawTrackedMeasurements();
  drawEdgeIndicators();
  drawDragPreview();
}

async function tick() {
  // Main browser loop: ask Python for a new state, draw it, then schedule the
  // next frame. If paused, we request zero physics steps.
  if (!state) {
    await fetchState(0);
    draw();
    requestAnimationFrame(tick);
    return;
  }

  if (viewingHistory && paused) {
    draw();
    requestAnimationFrame(tick);
    return;
  }

  if (!paused) {
    stepAccumulator += selectedStepRate();
  }
  const steps = paused ? 0 : Math.floor(stepAccumulator);
  stepAccumulator -= steps;
  await fetchState(steps);
  draw();
  requestAnimationFrame(tick);
}

toggleButton.addEventListener("click", () => {
  setPaused(!paused);
});

resetButton.addEventListener("click", () => {
  resetSimulation();
});

stepOnceButton.addEventListener("click", stepOnce);

addModeButton.addEventListener("click", () => {
  setAddMode(!addMode);
});

scenarioSelect.addEventListener("change", () => {
  resetSimulation();
});

canvas.addEventListener("pointerdown", (event) => {
  if (!addMode) {
    const body = findBodyAtScreen(event.clientX, event.clientY);
    if (!body && (event.button === 0 || event.button === 1 || event.button === 2)) {
      canvas.setPointerCapture(event.pointerId);
      panDrag = {
        x: event.clientX,
        y: event.clientY,
        offset: [...cameraOffset],
      };
    }
    return;
  }
  canvas.setPointerCapture(event.pointerId);
  dragStart = screenToWorld(event.clientX, event.clientY);
  dragCurrent = dragStart;
  setPaused(true);
});

canvas.addEventListener("contextmenu", (event) => {
  event.preventDefault();
});

canvas.addEventListener("click", (event) => {
  if (addMode || dragStart || panDrag) {
    return;
  }
  if (suppressNextClick) {
    suppressNextClick = false;
    return;
  }

  const body = findBodyAtScreen(event.clientX, event.clientY);
  if (body) {
    if (handleMeasurementBodyClick(body)) {
      return;
    }
    focusBody(body.name);
  }
});

canvas.addEventListener("dblclick", (event) => {
  const body = findBodyAtScreen(event.clientX, event.clientY);
  if (body) {
    focusBody(body.name);
    setActiveTab("inspect");
  }
});

canvas.addEventListener("pointermove", (event) => {
  if (panDrag && !dragStart) {
    hoverCard.hidden = true;
    const scale = worldScale();
    cameraOffset = [
      panDrag.offset[0] - (event.clientX - panDrag.x) / scale,
      panDrag.offset[1] - (event.clientY - panDrag.y) / scale,
    ];
    focusBodySelect.value = "__free__";
    draw();
    return;
  }

  if (!dragStart) {
    renderHoverCard(findBodyAtScreen(event.clientX, event.clientY), event.clientX, event.clientY);
    return;
  }
  hoverCard.hidden = true;
  dragCurrent = screenToWorld(event.clientX, event.clientY);
  draw();
});

canvas.addEventListener("pointerleave", () => {
  hoverCard.hidden = true;
  hoverBodyName = null;
});

canvas.addEventListener("pointerup", async (event) => {
  if (panDrag && !dragStart) {
    panDrag = null;
    suppressNextClick = true;
    return;
  }

  if (!dragStart) {
    return;
  }
  const end = screenToWorld(event.clientX, event.clientY);
  await addBody(dragStart, end);
  dragStart = null;
  dragCurrent = null;
  updateOrbitCalculator();
  draw();
});

canvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  const factor = event.deltaY > 0 ? 0.88 : 1.14;
  setZoomAroundScreenPoint(selectedZoom() * factor, event.clientX, event.clientY);
  updateHud();
  draw();
}, { passive: false });

speedInput.addEventListener("input", updateHud);
bodyPresetSelect.addEventListener("change", applyBodyPreset);
newMassInput.addEventListener("input", updateHud);
orbitEccentricityInput.addEventListener("input", updateHud);
zoomInput.addEventListener("input", () => {
  updateHud();
  draw();
});
orbitVelocityInput.addEventListener("input", () => {
  if (orbitVelocityInput.checked) {
    stationaryInput.checked = false;
  }
  updateAddGuide();
  draw();
});
stationaryInput.addEventListener("input", () => {
  if (stationaryInput.checked) {
    orbitVelocityInput.checked = false;
  }
  updateAddGuide();
  draw();
});
orbitTargetSelect.addEventListener("change", draw);
orbitTargetSelect.addEventListener("change", updateAddGuide);
orbitTargetSelect.addEventListener("change", () => updateOrbitCalculator(dragStart, dragCurrent));
focusBodySelect.addEventListener("change", () => {
  updateHud();
  draw();
});
focusModeSelect.addEventListener("change", () => {
  updateHud();
  draw();
});
edgeIndicatorsInput.addEventListener("input", draw);
velocityVectorsInput.addEventListener("input", draw);
accelerationVectorsInput.addEventListener("input", draw);
forceLinesInput.addEventListener("input", draw);
selectedPullInput.addEventListener("input", draw);
centerOfMassMarkerInput.addEventListener("input", draw);
closestPairLineInput.addEventListener("input", draw);
distanceUnitSelect.addEventListener("change", () => {
  updateHud();
  draw();
});
massUnitSelect.addEventListener("change", () => {
  updateHud();
});
trackDistanceButton.addEventListener("click", () => {
  setMeasurementMode(!measurementMode);
});
clearMeasurementsButton.addEventListener("click", clearTrackedMeasurements);
for (const button of tabButtons) {
  button.addEventListener("click", () => setActiveTab(button.dataset.tab));
}
fitSystemButton.addEventListener("click", fitSystemView);
resetViewButton.addEventListener("click", resetView);
clearAllTrailsButton.addEventListener("click", clearAllTrails);
saveSystemButton.addEventListener("click", saveSystem);
exportDataButton.addEventListener("click", exportData);
snapshotSystemButton.addEventListener("click", snapshotSystem);
rewindFrameButton.addEventListener("click", rewindFrame);
restoreFrameButton.addEventListener("click", restoreTimelineFrame);
trySmallerStepButton.addEventListener("click", () => {
  halveTimestep();
});
increaseStepButton.addEventListener("click", () => {
  doubleTimestep();
});
resetStepButton.addEventListener("click", () => {
  resetTimestep();
});
timelineInput.addEventListener("input", () => {
  if (stateHistory.length === 0) {
    return;
  }
  setPaused(true);
  timelineIndex = Number(timelineInput.value);
  state = structuredClone(stateHistory[timelineIndex]);
  viewingHistory = true;
  updateHud();
  draw();
});
loadSystemButton.addEventListener("click", () => loadSystemFileInput.click());
loadSystemFileInput.addEventListener("change", async () => {
  const [file] = loadSystemFileInput.files;
  if (file) {
    await loadSystemFromFile(file);
  }
  loadSystemFileInput.value = "";
});
for (const input of [editNameInput, editColorInput, editMassInput, editRadiusInput, editXInput, editYInput, editVxInput, editVyInput]) {
  input.addEventListener("focus", () => {
    setPaused(true);
  });
  input.addEventListener("input", markEditorDirty);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      applySelectedBodyEdit();
    }
  });
}
for (const button of document.querySelectorAll(".mass-preset")) {
  button.addEventListener("click", () => {
    editMassInput.value = button.dataset.mass;
    editRadiusInput.value = button.dataset.radius;
    markEditorDirty();
  });
}
applyBodyEditButton.addEventListener("click", applySelectedBodyEdit);
freezeBodyButton.addEventListener("click", freezeSelectedBody);
cloneBodyButton.addEventListener("click", cloneSelectedBody);
orbitSelectedButton.addEventListener("click", orbitAroundSelectedBody);
clearTrailButton.addEventListener("click", () => {
  editorDirty = false;
  clearSelectedTrail();
});
removeBodyButton.addEventListener("click", () => {
  editorDirty = false;
  removeSelectedBody();
});
collapseHudButton.addEventListener("click", () => {
  const panels = [...hud.querySelectorAll(".panel")];
  const shouldOpen = panels.some((panel) => !panel.open);
  for (const panel of panels) {
    panel.open = shouldOpen;
  }
  collapseHudButton.textContent = shouldOpen ? "Collapse" : "Expand";
});

hideHudButton.addEventListener("click", () => {
  hud.classList.add("hidden");
  showHudButton.hidden = false;
});

showHudButton.addEventListener("click", () => {
  hud.classList.remove("hidden");
  showHudButton.hidden = true;
});

hudDragHandle.addEventListener("pointerdown", (event) => {
  if (event.target.closest("button")) {
    return;
  }

  event.preventDefault();
  const rect = hud.getBoundingClientRect();
  hudDrag = {
    pointerId: event.pointerId,
    offsetX: event.clientX - rect.left,
    offsetY: event.clientY - rect.top,
  };
  hud.style.left = `${rect.left}px`;
  hud.style.top = `${rect.top}px`;
  hud.style.right = "auto";
  hud.style.width = `${rect.width}px`;
  document.body.classList.add("dragging-hud");
});

window.addEventListener("pointermove", (event) => {
  if (!hudDrag) {
    return;
  }

  event.preventDefault();
  const maxLeft = Math.max(8, window.innerWidth - hud.offsetWidth - 8);
  const maxTop = Math.max(8, window.innerHeight - hud.offsetHeight - 8);
  const left = Math.max(8, Math.min(maxLeft, event.clientX - hudDrag.offsetX));
  const top = Math.max(8, Math.min(maxTop, event.clientY - hudDrag.offsetY));
  hud.style.left = `${left}px`;
  hud.style.top = `${top}px`;
});

window.addEventListener("pointerup", () => {
  if (hudDrag) {
    document.body.classList.remove("dragging-hud");
  }
  hudDrag = null;
});

window.addEventListener("pointercancel", () => {
  document.body.classList.remove("dragging-hud");
  hudDrag = null;
});

window.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (key === "h") {
    const hidden = hud.classList.toggle("hidden");
    showHudButton.hidden = !hidden;
    return;
  }

  if (event.target.matches("input, select, textarea")) {
    return;
  }

  if (key === "f") {
    fitSystemView();
  } else if (key === "r") {
    resetView();
  } else if (key === ".") {
    stepOnce();
  } else if (event.key === "?") {
    setActiveTab("help");
  }
});
window.addEventListener("resize", () => {
  resizeCanvas();
  draw();
});

resizeCanvas();
setActiveTab("sim");
tick();
