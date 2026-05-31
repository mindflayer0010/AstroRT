"""AstroRT Phase 1 physics prototype.

This package exports only the small public surface we want beginners to touch
first: a `Body`, the gravitational constant `G`, and the `Simulation` wrapper.
Everything else remains importable from its module when we need details.
"""

from astro_rt.body import Body
from astro_rt.constants import G
from astro_rt.simulation import Simulation

__all__ = ["Body", "G", "Simulation"]
