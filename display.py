from interfaces import *


class Display:
    def __init__(self, rocket: Rocket, planets: Sequence[Planet]):
        self.rocket = rocket
        self.planets = planets

    @property
    def force(self) -> Vector2d:
        force = Vector2d([0, 0])
        for planet in self.planets:
            dist = self.rocket.position.dist(planet.position)
            magnitude = G * self.rocket.mass_ship * planet.mass / dist**3
            force += (planet.position - self.rocket.position) * magnitude
        return force


if __name__ == "__main__":
    r = Rocket(Vector2d(0, 0), 100, 0)
    planets = [
        Planet(Vector2d(10, 10), 100),
        Planet(Vector2d(0, 10), 100),
        Planet(Vector2d(10, 0), 100),
    ]
    d = Display(r, planets)
    print(d.force)
