import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

from astro_rt.body import Body
from astro_rt.vector import vec2
from astro_rt.simulation import Simulation

def main():
    sun = Body("Sun", 1.0, vec2(0, 0), vec2(0, 0))
    # Earth with mass 1.0
    earth = Body("Earth", 1.0, vec2(1, 0), vec2(0, 6.2831853)) # 2*pi

    sim = Simulation([sun, earth], dt=0.01)
    
    # run for 0.1 years
    sim.step(10)
    print("Sun pos:", sim.bodies[0].position)
    print("Earth pos:", sim.bodies[1].position)

if __name__ == "__main__":
    main()
