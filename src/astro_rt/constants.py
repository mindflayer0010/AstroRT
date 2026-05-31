"""Project-wide constants for Phase 1.

Units:
- distance: astronomical units (AU)
- mass: solar masses
- time: Earth years

In these normalized units, Earth's circular speed at 1 AU around a
1-solar-mass star is 2*pi AU/year, and G becomes 4*pi^2.
"""

from math import pi

# In normalized astronomy units, this value makes a 1 AU circular orbit around
# a 1 solar-mass star have speed 2*pi AU/year. That gives us readable numbers
# while preserving the shape of Newtonian gravity.
G = 4.0 * pi * pi
