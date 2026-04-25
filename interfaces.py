from dataclasses import dataclass
from typing import overload
from collections.abc import Sequence, Callable
from math import sqrt


# G = 6.6674e-11
G = 10
BASE_ANIMATION_STEPS = 10
NUM_ROCKET_MASS_POINTS = 5


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

    def mag(self):
        return sqrt(self.x**2 + self.y**2)

    # region: properties and dunder methods
    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, val: float):
        self.pos = val, self.pos[1]

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, val: float):
        self.pos = self.pos[0], val

    def __str__(self) -> str:
        return f"{self.x} {self.y}"

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
    angle: float
    velocity: Vector2d
    rotational_velocity: float
    mass_ship: float

    mass_fuel: float = 0
    speed_fuel: float = 0
    thrust: float = 0
    length: float = 0

    def __str__(self):
        return f"{self.position} {self.angle} {self.velocity} {self.rotational_velocity} {self.mass_ship} {self.mass_fuel} {self.speed_fuel} {self.thrust} {self.length}"


@dataclass
class Planet:
    position: Vector2d
    mass: float
    radius: float = 0

    def __str__(self):
        return f"{self.position.x} {self.position.y} {self.mass} {self.radius}"


def planet_from_str(string: str):
    l = list(map(float, string.split()))
    position = Vector2d(l[0], l[1])
    mass = l[2]
    radius = l[3]
    return Planet(position, mass, radius)


def point_from_str(str: str) -> tuple[Vector2d, float]:
    l = list(map(float, str.split()))
    return Vector2d(l[0], l[1]), l[2]


def rocket_from_str(str: str):
    l = list(map(float, str.split()))
    position = Vector2d(l[0], l[1])
    angle = l[2]
    velocity = Vector2d(l[3], l[4])
    rotational_velocity = l[5]
    ship_mass = l[6]
    fuel_mass = l[7]
    fuel_speed = l[8]
    thrust = l[9]
    length = l[10]
    return Rocket(
        position,
        angle,
        velocity,
        rotational_velocity,
        ship_mass,
        fuel_mass,
        fuel_speed,
        thrust,
        length,
    )
