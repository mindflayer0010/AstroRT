"""Phase 1 demo runner.

Run headless metrics:
    python -m astro_rt.demo --headless --scenario sun_earth --years 1

Run optional Pygame viewer:
    python -m astro_rt.demo --scenario sun_earth
"""

from __future__ import annotations

import argparse

from astro_rt.metrics import relative_error
from astro_rt.scenarios import SCENARIOS, load_scenario
from astro_rt.simulation import Simulation


def run_headless(scenario: str, years: float, dt: float) -> None:
    """Run a scenario without graphics and print validation metrics."""

    sim = Simulation(load_scenario(scenario), dt=dt)

    # Convert the requested duration into fixed steps. Rounding keeps
    # `--years 1` closer to one simulated year than truncation.
    steps = round(years / dt)
    start = sim.snapshot()

    for _ in range(steps):
        sim.step()

    end = sim.snapshot()
    print(f"Scenario: {scenario}")
    print(f"Simulated years: {sim.time:.3f}")
    print(f"Steps: {steps}")
    print(f"Initial energy: {start.energy:.12e}")
    print(f"Final energy:   {end.energy:.12e}")
    print(f"Relative energy drift: {relative_error(end.energy, start.energy):.12e}")
    print(f"Initial Lz: {start.angular_momentum_z:.12e}")
    print(f"Final Lz:   {end.angular_momentum_z:.12e}")
    print(f"Relative Lz drift: {relative_error(end.angular_momentum_z, start.angular_momentum_z):.12e}")


def run_viewer(scenario: str, dt: float) -> None:
    """Run the optional Pygame visualizer."""

    try:
        import pygame
    except ImportError:
        print("Pygame is not installed. Falling back to headless mode.")
        print("Install the viewer extra with: pip install -e .[viz]")
        run_headless(scenario, years=1.0, dt=dt)
        return

    pygame.init()
    width, height = 1000, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("AstroRT Phase 1")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    sim = Simulation(load_scenario(scenario), dt=dt)
    paused = False

    # More steps per frame makes simulated time pass faster, but also gives the
    # CPU more physics work to do before drawing the next frame.
    steps_per_frame = 2

    # Pixels per AU. The Pygame viewer stays intentionally simple; the browser
    # visualizer has the richer zoom/focus sandbox tools.
    scale = 180.0

    def to_screen(position):
        # Physics coordinates are centered at (0, 0). Screen coordinates start
        # at the top-left, so we shift by half the window size.
        x, y = position if isinstance(position, tuple) else position.as_tuple()
        return int(width / 2 + x * scale), int(height / 2 + y * scale)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Pygame controls are intentionally small: enough to inspect
                # physics quickly while the browser app handles sandbox editing.
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP:
                    steps_per_frame = min(200, steps_per_frame + 1)
                elif event.key == pygame.K_DOWN:
                    steps_per_frame = max(1, steps_per_frame - 1)
                elif event.key == pygame.K_r:
                    sim = Simulation(load_scenario(scenario), dt=dt)

        if not paused:
            sim.step(steps_per_frame)

        screen.fill((8, 10, 18))
        for body in sim.bodies:
            # Trails reveal orbital shape and drift better than dots alone.
            if len(body.trail) > 1:
                points = [to_screen(point) for point in body.trail[-500:]]
                pygame.draw.lines(screen, body.color, False, points, 1)
            pygame.draw.circle(screen, body.color, to_screen(body.position), int(body.radius))

        # The HUD shows physics health while the system runs.
        snap = sim.snapshot()
        lines = [
            f"scenario: {scenario}",
            f"time: {sim.time:.3f} years",
            f"steps/frame: {steps_per_frame}",
            f"energy drift: {relative_error(snap.energy, sim.initial_energy):.3e}",
            f"Lz drift: {relative_error(snap.angular_momentum_z, sim.initial_angular_momentum_z):.3e}",
            "space pause | up/down speed | r reset | esc quit",
        ]
        for i, line in enumerate(lines):
            screen.blit(font.render(line, True, (230, 235, 245)), (16, 16 + i * 22))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main() -> None:
    """Parse CLI arguments and choose headless or visual mode."""

    parser = argparse.ArgumentParser(description="Run AstroRT Phase 1.")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="sun_earth")
    parser.add_argument("--years", type=float, default=1.0)
    parser.add_argument("--dt", type=float, default=1.0 / 365.25)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    if args.headless:
        run_headless(args.scenario, args.years, args.dt)
    else:
        run_viewer(args.scenario, args.dt)


if __name__ == "__main__":
    main()
