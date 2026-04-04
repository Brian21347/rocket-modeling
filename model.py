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
            if abs(self.rocket.position.x - planet.position.x) + abs(self.rocket.position.y - planet.position.y) > planet.radius: 
                continue
            dist = self.rocket.position.dist(planet.position)
            if dist <= planet.radius:
                return planet
        return None

    def estimate_path(self):
        dmassfuel = -self.rocket.thrust.mag() / self.rocket.speed_fuel * self.dt
        for _ in tqdm.tqdm(range(self.simulation_seconds // self.dt)):
            if self.rocket.mass_fuel == 0:
                thrust = Vector2d(0, 0)
            elif self.rocket.mass_fuel - dmassfuel < 0:
                thrust_percent = self.rocket.mass_fuel / -dmassfuel
                thrust = self.rocket.thrust * thrust_percent
                self.rocket.mass_fuel = 0
            else:
                thrust = self.rocket.thrust
                self.rocket.mass_fuel += dmassfuel

            self.rocket.velocity += (
                (self.calc_force() + thrust)
                * self.dt
            )
            self.rocket.position += self.rocket.velocity * self.dt
            self.path.append(self.rocket.position)
            if (crash_dest := self.crash_checking()) != None:
                return crash_dest

    def calc_force(self) -> Vector2d:
        force = Vector2d([0, 0])
        for planet in self.planets:
            dist = self.rocket.position.dist(planet.position)
            magnitude = G * planet.mass / dist**3
            force += (planet.position - self.rocket.position) * magnitude
        return force


if __name__ == "__main__":
    r = Rocket(Vector2d(6.37001e6, 0), Vector2d(0, 0), 3e6, 2.5e6, 2400, Vector2d(33e4, 0))
    planets = [
        Planet(Vector2d(0, 0), 6e24, 6.37e6),
        Planet(Vector2d(0, 2.25e8), 6e24, 6.37e6),
        Planet(Vector2d(5e8, 4e8), 6e24, 6.37e6),
        Planet(Vector2d(11e8, 6e8), 6e24, 6.37e6),
        Planet(Vector2d(15e8, 15e8), 6e24, 6.37e6),
    ]
    # m = Model(r, planets, 5_000, 10)
    # m.estimate_path()
    # m.save_path("test_paths/test_.path", overwrite=True)
    m = Model("test_paths/test_.path", 10_000)
    m.estimate_path()
    m.save_path("test_paths/test_.path", overwrite=False)
