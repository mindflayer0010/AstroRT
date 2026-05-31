"""Small 2D vector type.

This keeps Phase 1 runnable without third-party packages and mirrors the kind
of Vec2 type we will later write in C++.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Vec2:
    """A tiny immutable 2D vector.

    `frozen=True` means operations return new vectors instead of mutating the
    current one. That makes the math easier to reason about while we learn.
    """

    # x and y are the two coordinates of a 2D quantity. They can mean position,
    # velocity, acceleration, or any other vector depending on context.
    x: float
    y: float

    def __add__(self, other: "Vec2") -> "Vec2":
        # Vector addition: move right/left by x and up/down by y.
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        # Vector subtraction gives the direction from `other` to `self`.
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        # Scalar multiplication changes vector size without changing direction.
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vec2":
        return self * scalar

    def __truediv__(self, scalar: float) -> "Vec2":
        return Vec2(self.x / scalar, self.y / scalar)

    def dot(self, other: "Vec2") -> float:
        # Dot product is used for squared distance: v dot v = x*x + y*y.
        return self.x * other.x + self.y * other.y

    def norm(self) -> float:
        # Norm is the vector length, also called magnitude.
        return sqrt(self.dot(self))

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    def as_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


ZERO = Vec2(0.0, 0.0)


def vec2(x: float, y: float) -> Vec2:
    """Convenience constructor that normalizes inputs to floats."""

    return Vec2(float(x), float(y))
