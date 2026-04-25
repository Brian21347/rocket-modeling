from interfaces import *
import tqdm
from os.path import join, exists
from os import SEEK_END, SEEK_CUR
import datetime
from typing import overload
import sys
from math import pi, sin, cos


class Model:
    # region: inits
    @overload
    def __init__(
        self,
        rocket: Rocket,
        planets: Sequence[Planet],
        simulation_hours: float,
        dt: float,
        /,
    ): ...

    @overload
    def __init__(self, path: str, simulation_hours: float, /): ...

    def __init__(self, *args) -> None:
        if len(args) == 4:
            self.rocket = args[0]
            self.planets = args[1]
            self.simulation_seconds = args[2] * 3_600
            self.dt = args[3]  # units: seconds
            self.path: list[tuple[Vector2d, float]] = []
        elif len(args) == 2:
            path = args[0]
            if not exists(path):
                raise FileNotFoundError(f"{path} not found")
            self.load_from_path(path)
            self.simulation_seconds = args[1] * 3_600
            self.path: list[tuple[Vector2d, float]] = []
        else:
            raise ValueError("Incorrect number of arguments provided")

        self.djs = [
            (-1 / 2 + j / (NUM_ROCKET_MASS_POINTS - 1)) * self.rocket.length
            for j in range(NUM_ROCKET_MASS_POINTS)
        ]
        self.mass_point_squared_sum = sum(dj**2 for dj in self.djs)
        self.d_mass_fuel = -self.rocket.thrust / self.rocket.speed_fuel
        self.d_rotational_inertia = (
            self.d_mass_fuel / NUM_ROCKET_MASS_POINTS * self.mass_point_squared_sum
        )

    # endregion

    def load_from_path(self, path):
        # read header
        with open(path) as f:
            self.dt = float(f.readline())
            self.planets = []
            n_planets = int(f.readline())
            for _ in range(n_planets):
                planet = planet_from_str(f.readline())
                self.planets.append(planet)

        # read rocket position
        with open(path, mode="rb") as f:
            f.seek(-2, SEEK_END)  # skip \n at end of file
            while f.read(1) != b"\n":
                f.seek(-2, SEEK_CUR)
            line = f.readline().decode()
            self.rocket = rocket_from_str(line)

    def save_path(self, path: str | None = None, overwrite=False):
        SAVE_PATH = "paths"

        if not self.path:
            raise ValueError("Path not created")

        now = datetime.datetime.now()
        if path is None:
            path = join(
                SAVE_PATH, f"{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}.path"
            )
        if not exists(path) or overwrite:
            with open(path, mode="w") as f:
                f.write(str(self.dt) + "\n")
                f.write(str(len(self.planets)) + "\n")
                for planet in self.planets:
                    f.write(str(planet) + "\n")
        with open(path, mode="a") as f:
            for position in self.path[:-1:BASE_ANIMATION_STEPS]:
                pos, angle = position
                f.write(str(pos) + " " + str(angle) + "\n")
            f.write(str(self.rocket) + "\n")

    def crash_checking(self) -> Planet | None:
        for planet in self.planets:
            if (
                abs(self.rocket.position.x - planet.position.x)
                + abs(self.rocket.position.y - planet.position.y)
                > planet.radius
            ):
                continue
            dist = self.rocket.position.dist(planet.position)
            if dist <= planet.radius:
                return planet
        return None

    def estimate_path(self) -> Planet | None:
        prev = 0
        self.path.append((self.rocket.position, self.rocket.angle))
        for iteration in tqdm.tqdm(range(int(self.simulation_seconds // self.dt))):
            self.update_angle()
            self.update_pos()
            if iteration - prev == BASE_ANIMATION_STEPS:
                self.path.append((self.rocket.position, self.rocket.angle))
                prev = iteration
            if (crash_dest := self.crash_checking()) != None:
                return crash_dest

    def update_pos(self):
        if self.rocket.mass_fuel == 0:
            thrust = 0
            self.d_mass_fuel = 0
        elif self.rocket.mass_fuel + self.d_mass_fuel * self.dt < 0:
            thrust_percent = self.rocket.mass_fuel / -self.d_mass_fuel / self.dt
            thrust = self.rocket.thrust * thrust_percent
            self.rocket.mass_fuel = 0
            self.d_mass_fuel = 0
        else:
            thrust = self.rocket.thrust
            self.rocket.mass_fuel += self.d_mass_fuel * self.dt

        thrust_vec = Vector2d(cos(self.rocket.angle), sin(self.rocket.angle)) * thrust
        self.rocket.velocity += (
            thrust_vec / self.rocket_mass
            + self.calc_force()
            - self.d_mass_fuel / self.rocket_mass * self.rocket.velocity
        ) * self.dt
        self.rocket.position += self.rocket.velocity * self.dt

    def update_angle(self):
        rot_inertia = self.rocket_mass / NUM_ROCKET_MASS_POINTS * self.mass_point_squared_sum
        d_rot_inertia = self.d_mass_fuel / NUM_ROCKET_MASS_POINTS * self.mass_point_squared_sum
        self.rocket.rotational_velocity += (
            (self.calc_torque() - d_rot_inertia * self.rocket.rotational_velocity)
            / rot_inertia
            * self.dt
        )
        self.rocket.angle += self.rocket.rotational_velocity * self.dt

    def calc_force(self) -> Vector2d:
        force = Vector2d([0, 0])
        for planet in self.planets:
            dist = self.rocket.position.dist(planet.position)
            try:
                force += (planet.position - self.rocket.position) * planet.mass / dist**3
            except:
                sys.exit()
        return G * force

    def calc_torque(self) -> float:
        torque: float = 0
        for j in range(NUM_ROCKET_MASS_POINTS):
            heading = Vector2d(cos(self.rocket.angle), sin(self.rocket.angle))
            t_heading = Vector2d(-sin(self.rocket.angle), cos(self.rocket.angle))

            force = Vector2d(0, 0)
            for planet in self.planets:
                planet: Planet
                nom = planet.mass * (planet.position - self.rocket.position)
                denom = (self.rocket.position + self.djs[j] * heading - planet.position).mag() ** 3
                force += nom / denom

            torque += self.djs[j] * (t_heading.x * force.x + t_heading.y * force.y)
        return torque * G * self.rocket_mass / NUM_ROCKET_MASS_POINTS

    @property
    def rocket_mass(self):
        return self.rocket.mass_fuel + self.rocket.mass_ship


if __name__ == "__main__":
    # r = Rocket(Vector2d(0, 0), -3 * pi / 4, Vector2d(0, 0), 0, 100, 100, 3e-5, 1e-8, 20)
    # planets = [
    #     Planet(Vector2d(10, 10), 100, 2),
    #     Planet(Vector2d(25, 60), 100, 2),
    #     Planet(Vector2d(50, 90), 100, 2),
    #     Planet(Vector2d(100, 100), 100, 2),
    # ]
    r = Rocket(Vector2d(30, 20), -7 * pi / 16, Vector2d(0, 0), 0, 4, 10, 4, 6, 1)
    planets = [
        Planet(Vector2d(0, 0), 50, 2),
        Planet(Vector2d(60, 0), 50, 2),
        Planet(Vector2d(30, 45), 50, 2),
    ]
    path = "test_paths/test3.path"

    # m = Model(r, planets, 0.010, 0.0001)
    # m.estimate_path()
    # m.save_path(path, overwrite=True)

    m = Model(path, 0.010)
    m.estimate_path()
    m.save_path(path, overwrite=False)
