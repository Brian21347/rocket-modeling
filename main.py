import model
from interfaces import *
import visualize
import os

if __name__ == "__main__":
    r = Rocket(Vector2d(0, 0), 100, Vector2d(0, sqrt(10 * G)), mass_fuel=0, speed_fuel=10, thrust=Vector2d(0, 1e-8))
    planets = [
        Planet(Vector2d(10, 10), 100, 10),
        Planet(Vector2d(0, 10), 100, 10),
        Planet(Vector2d(10, 0), 100, 10),
    ]
    PATH = os.path.join("paths", "test.path")
    m = model.Model(r, planets)
    m.estimate_path_with_mass_update()
    m.save_path(PATH)

    
    v = visualize.Visualize(PATH)
    v.run()
