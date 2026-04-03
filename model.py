from interfaces import *
import tqdm
from os.path import join
import datetime

class Model:
    def __init__(self, rocket: Rocket, 
                 planets: Sequence[Planet], 
                 simulation_seconds: int = 1000 * 3600, 
                 dt: int = 10):
        self.rocket = rocket
        self.planets = planets
        self.path = []
        self.simulation_seconds = simulation_seconds
        self.dt = dt  # units: seconds

    def save_path(self, path: str | None = None):
        SAVE_PATH = "paths"

        if not self.path:
            raise ValueError("Path not created")

        now = datetime.datetime.now()
        if path is None:
            path = join(SAVE_PATH, f"{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}.path")

        with open(path, mode="w") as f:
            f.write(str(self.dt) + "\n")
            f.write(str(len(self.planets)) + "\n")
            for planet in self.planets:
                f.write(str(planet) + "\n")
            for position in self.path:
                f.write(str(position) + "\n")

    def estimate_path(self):
        for _ in tqdm.tqdm(range(self.simulation_seconds//self.dt)):
            self.rocket.velocity += self.calc_force() / self.rocket.mass_ship * self.dt
            self.rocket.position += self.rocket.velocity * self.dt
            self.path.append(self.rocket.position)

    def estimate_path_with_mass_update(self):
        for _ in tqdm.tqdm(range(self.simulation_seconds//self.dt)):
            thrust = Vector2d(0,0)
            if self.rocket.mass_fuel > 0:
                thrust = self.rocket.thrust
                """
                dM * speed_fuel - M dV = 0
                since thurst = | M dV/dt |
                dM * speed_fuel = | thurst | * dt
                """
                dmassfuel = - thrust.mag() / self.rocket.speed_fuel * self.dt
                self.rocket.mass_fuel += dmassfuel

            self.rocket.velocity += (self.calc_force() + self.rocket.thrust) / (self.rocket.mass_ship + self.rocket.mass_fuel) * self.dt
            self.rocket.position += self.rocket.velocity * self.dt
            self.path.append(self.rocket.position)

    def calc_force(self) -> Vector2d:
        force = Vector2d([0, 0])
        for planet in self.planets:
            dist = max(self.rocket.position.dist(planet.position), 1e-3)
            magnitude = G * self.rocket.mass_ship * planet.mass / dist**3
            force += (planet.position - self.rocket.position) * magnitude
        return force


if __name__ == "__main__":
    r = Rocket(Vector2d(0, 0), 100, Vector2d(0, sqrt(10 * G)))
    planets = [
        Planet(Vector2d(10, 10), 100, 10),
        Planet(Vector2d(0, 10), 100, 10),
        Planet(Vector2d(10, 0), 100, 10),
    ]
    m = Model(r, planets)
    m.estimate_path()
    m.save_path()
