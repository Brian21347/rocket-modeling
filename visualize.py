import pygame
import sys
from interfaces import *
from os.path import join


class Visualize:
    def __init__(self, file_path: str):
        pygame.init()
        self.FRAME_RATE = 60
        self.clock = pygame.time.Clock()
        self.time_i = 0
        self.multi = 2
        self.step_size = 100  # speed
        self.screen_size = [500, 500]
        self.path_drawing = pygame.Surface(self.screen_size)
        self.path_drawing.fill("light gray")
        self.screen = pygame.display.set_mode(self.screen_size)
        self.gen = self.time_step()
        self.offset = Vector2d(0, 0)
        self.margin = Vector2d(50, 50)
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
        self.offset -= self.margin
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
        while 0 <= self.time_i < len(self.path):
            yield self.path[self.time_i]
            self.time_i += self.step_size
        if self.time_i < 0:
            self.time_i = 0
        if self.time_i >= len(self.path):
            self.time_i = len(self.path) - 1
        self.step_size = 0

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
                    if event.key == pygame.K_UP:
                        self.step_size += 100
                    elif event.key == pygame.K_DOWN:
                        self.step_size -= 100
                    elif event.key == pygame.K_SPACE:
                        self.step_size = 0
                    elif event.key == pygame.K_LEFT:
                        self.time_i = len(self.path) - 1
                        self.step_size = 0
                    elif event.key == pygame.K_RIGHT:
                        self.time_i = 0
                        self.step_size = 0
            self.draw()
            self.clock.tick(self.FRAME_RATE)
    
    def draw_planets(self):
        for planet in self.planets:
            planet: Planet
            pygame.draw.circle(self.path_drawing, "dark gray", (planet.position - self.offset).pos, planet.radius)

    def draw_path(self):
        try:
            n_pos = next(self.gen)
            pygame.draw.line(self.path_drawing, "red", (self.pos - self.offset).pos, (n_pos - self.offset).pos)
            self.pos = n_pos
        except StopIteration:
            self.gen = self.time_step()
    
    def draw(self):
        self.draw_path()
        self.screen.blit(self.path_drawing, [0,0])
        pygame.draw.circle(self.screen, "black", (self.pos - self.offset).pos, 5)
        pygame.display.flip()
                        

if __name__ == "__main__":
    v = Visualize(join("paths", "triple_planet.path"))
    v.run()

