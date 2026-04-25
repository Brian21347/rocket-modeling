from interfaces import *
import tqdm
from math import sin, cos


class Model:
    def __init__(
        self,
        rocket: Rocket,
        planets: Sequence[Planet],
        simulation_hours: float,
        dt: float,
        /,
    ): 
        self.rocket = rocket
        self.planets = planets
        self.simulation_seconds = simulation_hours * 3_600
        self.dt = dt
        self.path: list[tuple[Vector2d, float]] = []

        self.djs = [
            (-1 / 2 + j / (NUM_ROCKET_MASS_POINTS - 1)) * self.rocket.length
            for j in range(NUM_ROCKET_MASS_POINTS)
        ]
        self.mass_point_squared_sum = sum(dj**2 for dj in self.djs)
        self.d_mass_fuel = -self.rocket.thrust / self.rocket.speed_fuel
        self.d_rotational_inertia = (
            self.d_mass_fuel / NUM_ROCKET_MASS_POINTS * self.mass_point_squared_sum
        )

    def estimate_path(self) -> Planet | None:
        prev = 0
        self.path.append((self.rocket.position, self.rocket.angle))
        for iteration in tqdm.tqdm(range(int(self.simulation_seconds // self.dt))):
            self.update_angle()
            self.update_pos()
            if iteration - prev == BASE_ANIMATION_STEPS:
                self.path.append((self.rocket.position, self.rocket.angle))
                prev = iteration

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
            force += (planet.position - self.rocket.position) * planet.mass / dist**3
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
