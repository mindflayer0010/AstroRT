from dataclasses import dataclass

@dataclass(frozen=True)
class Vec2:
    x: float
    y: float
    def __add__(self, o): return Vec2(self.x+o.x, self.y+o.y)
    def __sub__(self, o): return Vec2(self.x-o.x, self.y-o.y)

ZERO = Vec2(0,0)
b = [ZERO, ZERO, ZERO]
b[0] += Vec2(1,1)
b[1] -= Vec2(2,2)
print(b)
