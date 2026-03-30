import pygame
import sys
from interfaces import *


class Visualize:
    def __init__(self, file_path: str):
        pygame.init()
        self.FRAME_RATE = 60
        self.clock = pygame.time.Clock()
        self.time_i = 0
        self.multi = 30
        self.step_size = 100  # speed
        self.screen_size = [500, 500]
        self.path_drawing = pygame.Surface(self.screen_size)
        self.path_drawing.fill("light gray")
        self.screen = pygame.display.set_mode(self.screen_size)
        self.gen = self.time_step()
        self.offset = Vector2d(0, 0)
        with open(file_path) as f:
            self.dt = int(f.readline())
            self.planets = []
            n_planets = int(f.readline())
            for _ in range(n_planets):
                self.planets.append(self.planet_from_str(f.readline()))
            self.path = []
            while (line := f.readline()) != "":
                point = self.point_from_str(line)
                self.offset.x = min(point.x, self.offset.x)
                self.offset.y = min(point.y, self.offset.y)
                self.path.append(point)
        self.pos = self.path[0]
        self.draw_planets()


    # region: input
    def planet_from_str(self, string: str):
        l = list(map(float, string.split()))
        position = Vector2d(l[0] * self.multi, l[1] * self.multi)
        mass = l[2]
        radius = l[3]
        return Planet(position, mass, radius)
    
    def point_from_str(self, str: str):
        a, b = map(float, str.split())
        return Vector2d(a * self.multi, b * self.multi)
    # endregion
    
    def time_step(self):
        while self.time_i < len(self.path):
            yield self.path[self.time_i]
            self.time_i += self.step_size

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            self.draw()
            self.clock.tick(self.FRAME_RATE)
    
    def draw_planets(self):
        for planet in self.planets:
            planet: Planet
            pygame.draw.circle(self.path_drawing, "dark gray", planet.position.pos, planet.radius)

    def draw_path(self):
        try:
            n_pos = next(self.gen)
            pygame.draw.line(self.path_drawing, "red", (self.pos + self.offset).pos, (n_pos + self.offset).pos)
            self.pos = n_pos
        except StopIteration:
            sys.exit()
    
    def draw(self):
        self.draw_path()
        self.screen.blit(self.path_drawing, [0,0])
        pygame.display.flip()
                        

if __name__ == "__main__":
    v = Visualize("paths\\3_30_13_42_8.path")
    v.run()

