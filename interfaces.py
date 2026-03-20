from dataclasses import dataclass
from typing import overload
from collections.abc import Sequence, Callable
from math import sqrt


G = 6.6674e-11


class Vector2d:
    pos: tuple[float, float]

    # region: init
    @overload
    def __init__(self, x: float, y: float, /) -> None: ...

    @overload
    def __init__(self, pos: Sequence[float,], /) -> None: ...

    def __init__(self, *args) -> None:
        if len(args) > 2:
            raise ValueError()
        if len(args) == 1:
            self.pos = tuple(args[0])
        elif len(args) == 2:
            self.pos = args

    # endregion

    def dist(self, other: "Vector2d"):
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    # region: properties and dunder methods
    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    def __str__(self) -> str:
        return str(self.pos)

    def __add__(self, other: "Vector2d"):
        return Vector2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2d"):
        return Vector2d(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float):
        return Vector2d(self.x * other, self.y * other)

    def __rmul__(self, other: float):
        return self * other

    def __truediv__(self, other: float):
        return Vector2d(self.x / other, self.y / other)

    # endregion


@dataclass
class Rocket:
    position: Vector2d
    mass_ship: float
    initial_velocity: float

    mass_fuel: float = 0
    velocity_fuel: float = 0


@dataclass
class Planet:
    position: Vector2d
    mass: float
    radius: float = 0
    air_density_func: Callable[[int], int] = lambda dist: 0
