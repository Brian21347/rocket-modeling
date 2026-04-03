from interfaces import *
import tqdm
from os.path import join, exists
from os import SEEK_END, SEEK_CUR
import datetime
from typing import overload


class Model:
    # region: inits
    @overload
    def __init__(
        self,
        rocket: Rocket,
        planets: Sequence[Planet],
        simulation_hours: int,
        dt: int,
        /,
    ): ...

    @overload
    def __init__(self, path: str, simulation_hours: int, /): ...

    def __init__(self, *args) -> None:
        if len(args) == 4:
            self.rocket = args[0]
            self.planets = args[1]
            self.simulation_seconds = args[2] * 3_600
            self.dt = args[3]  # units: seconds
            self.path = []
            return
        if len(args) == 2:
            path = args[0]
            if not exists(path):
                raise FileNotFoundError(f"{path} not found")
            self.load_from_path(path)
            self.simulation_seconds = args[1] * 3_600
            self.path = []
            return
        raise ValueError("Incorrect number of arguments provided")
    # endregion
    
    def load_from_path(self, path):
        # read header
        with open(path) as f:
            self.dt = int(f.readline())
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
                f.write(str(position) + "\n")
            f.write(str(self.rocket) + "\n")

    def crash_checking(self):
        for planet in self.planets:
            dist = self.rocket.position.dist(planet.position)
            if dist <= planet.radius:
                return planet
        return None

    def estimate_path(self):
        for _ in tqdm.tqdm(range(self.simulation_seconds // self.dt)):
            self.rocket.velocity += self.calc_force() / self.rocket.mass_ship * self.dt
            self.rocket.position += self.rocket.velocity * self.dt
            self.path.append(self.rocket.position)
            if (crash_dest := self.crash_checking()) != None:
                return crash_dest

    def estimate_path_with_mass_update(self):
        crash_dest = None
        for _ in tqdm.tqdm(range(self.simulation_seconds // self.dt)):
            thrust = Vector2d(0, 0)
            if self.rocket.mass_fuel > 0:
                thrust = self.rocket.thrust
                """
                dM * speed_fuel - M dV = 0
                since thrust = | M dV/dt |
                dM * speed_fuel = | thrust | * dt
                """
                dmassfuel = -thrust.mag() / self.rocket.speed_fuel * self.dt
                self.rocket.mass_fuel += dmassfuel

            self.rocket.velocity += (
                (self.calc_force() + self.rocket.thrust)
                / (self.rocket.mass_ship + self.rocket.mass_fuel)
                * self.dt
            )
            self.rocket.position += self.rocket.velocity * self.dt
            self.path.append(self.rocket.position)
            if (crash_dest := self.crash_checking()) != None:
                return crash_dest

    def calc_force(self) -> Vector2d:
        force = Vector2d([0, 0])
        for planet in self.planets:
            dist = max(self.rocket.position.dist(planet.position), 1e-3)
            magnitude = G * self.rocket.mass_ship * planet.mass / dist**3
            force += (planet.position - self.rocket.position) * magnitude
        return force


if __name__ == "__main__":
    r = Rocket(Vector2d(0, 0), Vector2d(0, sqrt(10 * G)), 100)
    planets = [
        Planet(Vector2d(10, 10), 100, 2),
        Planet(Vector2d(25, 60), 100, 2),
        Planet(Vector2d(50, 90), 100, 2),
        Planet(Vector2d(100, 100), 100, 2),
    ]
    # m = Model(r, planets, 1_000, 10)
    # m.estimate_path()
    # m.save_path("test_paths/test_.path", overwrite=True)
    for _ in range(10):
        m = Model("test_paths/test_.path", 1_000)
        m.estimate_path()
        m.save_path("test_paths/test_.path", overwrite=False)
