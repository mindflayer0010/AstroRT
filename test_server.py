import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

from astro_rt.server import BrowserSimulationApp

def main():
    app = BrowserSimulationApp("sun_earth")
    # Step a bit
    app.step(10)
    
    # Add a massive body
    payload = {
        "name": "Sun 2",
        "mass": 1.0,
        "x": 0.0,
        "y": 2.0,
        "vx": 0.0,
        "vy": 0.0
    }
    app.add_body(payload)
    
    # Check if Earth accelerates towards Sun 2
    for _ in range(10):
        state = app.step(1)
        for b in state["bodies"]:
            if b["name"] == "Earth":
                print("Earth Pos:", b["position"], "Acc:", b["acceleration"])

if __name__ == "__main__":
    main()
