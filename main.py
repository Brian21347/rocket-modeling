import model
from interfaces import *
from visualize import Visualize
import os
from math import pi, sin, cos


def main():
    speed = sqrt(10 * G)
    step_size = pi / 32
    # angles are reversed in pygame because down is positive.
    # 3pi/4, pi/4

    # check which planet is being crashed into and then stop the simulations at that point.
    # "Iterative deepening + bfs" to identify the angle at which the rocket would be successful.
    # simulate at a depth, then increase the
    # Likely to find the best path in terms of travel time.
    planets = [
        Planet(Vector2d(10, 10), 100, 2),
        Planet(Vector2d(25, 60), 100, 2),
        Planet(Vector2d(50, 90), 100, 2),
        Planet(Vector2d(100, 100), 100, 2),
    ]
    target_planet = planets[-1]
    for int_angle in range(8, 24, 1):
        angle = int_angle * step_size
        r = Rocket(Vector2d(0, 0), Vector2d(speed * cos(angle), speed * sin(angle)), 100)
        PATH = os.path.join("test_paths", f"{int_angle}.path")
        m = model.Model(r, planets, 1_000, 10)
        crash_dest = m.estimate_path_with_mass_update()
        if crash_dest is not None and crash_dest.position == target_planet.position:
            print("Reached target!")
            v = Visualize(PATH)
            v.run()
            m.save_path(PATH)
            break
        m.save_path(PATH)


if __name__ == "__main__":
    main()
