from interfaces import *
import tqdm


class Model:
    def __init__(
        self,
        rocket: Rocket,
        planets: Sequence[Planet],
        simulation_hours: int,
        dt: int,
    ) -> None:
        self.rocket = rocket
        self.planets = planets
        self.simulation_seconds = simulation_hours
        self.dt = dt
        self.path = []

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
        dmassfuel = -self.rocket.thrust.mag() / self.rocket.speed_fuel * self.dt
        self.path.append(self.rocket.position)
        for _ in tqdm.tqdm(range(self.simulation_seconds // self.dt)):
            if self.rocket.mass_fuel == 0:
                thrust = Vector2d(0, 0)
            elif self.rocket.mass_fuel + dmassfuel < 0:
                thrust_percent = self.rocket.mass_fuel / -dmassfuel
                thrust = self.rocket.thrust * thrust_percent
                self.rocket.mass_fuel = 0
            else:
                thrust = self.rocket.thrust
                self.rocket.mass_fuel += dmassfuel

            rocket_mass = self.rocket.mass_fuel + self.rocket.mass_ship
            self.rocket.velocity += (
                thrust / rocket_mass
                + self.calc_force()
                - dmassfuel / rocket_mass * self.rocket.velocity
            ) * self.dt
            self.rocket.position += self.rocket.velocity * self.dt
            self.path.append(self.rocket.position)
            if (crash_dest := self.crash_checking()) != None:
                return crash_dest

    def calc_force(self) -> Vector2d:
        force = Vector2d([0, 0])
        for planet in self.planets:
            dist = self.rocket.position.dist(planet.position)
            force += (planet.position - self.rocket.position) * planet.mass / dist**3
        return G * force
