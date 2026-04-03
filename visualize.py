import pygame
from interfaces import *
from os.path import join
import colorsys
from PIL import Image


class Visualize:
    def __init__(self, file_path: str):
        LINES = 8_000_000

        pygame.init()
        self.FRAME_RATE = 60
        self.clock = pygame.time.Clock()
        self.time_i = 0
        self.step_size = 1  # speed
        self.screen_size = Vector2d(500, 500)
        self.path_drawing = pygame.Surface(self.screen_size.pos)
        self.path_drawing.fill("light gray")
        self.screen = pygame.display.set_mode(self.screen_size.pos)
        self.gen = self.time_step()
        self.offset = Vector2d(0, 0)
        self.max_points = Vector2d(0, 0)
        # self.margin = Vector2d(50, 50)
        with open(file_path) as f:
            self.dt = int(f.readline())
            self.planets = []
            n_planets = int(f.readline())
            for _ in range(n_planets):
                planet = planet_from_str(f.readline())
                self.offset.x = min(planet.position.x, self.offset.x)
                self.max_points.x = max(planet.position.x, self.max_points.x)
                self.offset.y = min(planet.position.y, self.offset.y)
                self.max_points.y = max(planet.position.y, self.max_points.y)
                self.planets.append(planet)

            self.path = []
            while len(lines := f.readlines(LINES)) != 0:
                for line in lines:
                    point = point_from_str(line)
                    self.offset.x = min(point.x, self.offset.x)
                    self.max_points.x = max(point.x, self.max_points.x)
                    self.offset.y = min(point.y, self.offset.y)
                    self.max_points.y = max(point.y, self.max_points.y)
                    self.path.append(point)
        x_span = self.max_points.x - self.offset.x
        y_span = self.max_points.y - self.offset.y
        self.pos = self.path[0]
        self.multi = min(self.screen_size.x / x_span, self.screen_size.y / y_span)
        print(self.multi)
        self.offset *= self.multi
        self.path = [point * self.multi for point in self.path]
        self.planets = [
            Planet(planet.position * self.multi, planet.mass, planet.radius * self.multi)
            for planet in self.planets
        ]
        self.draw_planets()

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
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if event.key == pygame.K_UP:
                        self.step_size += 1
                    elif event.key == pygame.K_DOWN:
                        self.step_size -= 1
                    elif event.key == pygame.K_SPACE:
                        self.step_size = 0
                    elif event.key == pygame.K_LEFT:
                        self.time_i = 0
                        self.step_size = 0
                    elif event.key == pygame.K_RIGHT:
                        self.time_i = len(self.path) - 1
                        self.step_size = 0
            self.draw()
            self.clock.tick(self.FRAME_RATE)

    def save_animation(self, save_path: str):
        TIME_LIMIT = 10  # seconds
        FPS = 60
        FRAMES = TIME_LIMIT * FPS
        images = []
        self.step_size = max(len(self.path) // FRAMES, 1)
        self.path
        while self.time_i < len(self.path) - 1:
            image = Image.frombytes(
                "RGB",
                (int(self.screen_size.x), int(self.screen_size.y)),
                pygame.image.tobytes(self.screen, "RGB"),
            )
            self.draw(True)
            images.append(image)

        print("Saving animation...")
        images[0].save(save_path, save_all=True, append_images=images[1:], duration=50)

    def get_color(self, target_luminance=0.6):
        rgb = colorsys.hsv_to_rgb(self.time_i / len(self.path), 1, 1)
        r, g, b = rgb
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

        scale = target_luminance / luminance

        r_norm = min(1.0, r * scale)
        g_norm = min(1.0, g * scale)
        b_norm = min(1.0, b * scale)

        return (int(r_norm * 255), int(g_norm * 255), int(b_norm * 255))

    def draw_planets(self):
        for planet in self.planets:
            planet: Planet
            pygame.draw.circle(
                self.path_drawing,
                "dark gray",
                (planet.position - self.offset).pos,
                max(planet.radius, 2),
            )

    def draw_path(self, high_fidelity):
        try:
            if high_fidelity:
                for i in range(self.time_i + 1, self.time_i + self.step_size):
                    if i == len(self.path):
                        break
                    n_pos = self.path[i]
                    pygame.draw.line(
                        self.path_drawing,
                        self.get_color(),
                        (self.pos - self.offset).pos,
                        (n_pos - self.offset).pos,
                    )
                    self.pos = n_pos
            n_pos = next(self.gen)
                
            pygame.draw.line(
                self.path_drawing,
                self.get_color(),
                (self.pos - self.offset).pos,
                (n_pos - self.offset).pos,
            )
            self.pos = n_pos
        except StopIteration:
            self.gen = self.time_step()

    def draw(self, high_fidelity=False):
        self.draw_path(high_fidelity)
        self.screen.blit(self.path_drawing, [0, 0])
        pygame.draw.circle(self.screen, "black", (self.pos - self.offset).pos, 5)
        pygame.display.flip()


if __name__ == "__main__":
    v = Visualize(join("test_paths", "test_.path"))
    # v.run()
    v.save_animation(join("animations", "test.gif"))
