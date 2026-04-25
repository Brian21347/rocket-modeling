import pygame
from interfaces import *
from os.path import join
import colorsys
from PIL import Image
from math import pi


class Visualize:
    def __init__(self, file_path: str):
        LINES = 8_000_000

        pygame.init()
        pygame.key.set_repeat(200, 100)
        self.FRAME_RATE = 60
        self.clock = pygame.time.Clock()
        self.time_i = 0
        self.step_size = 1  # speed
        self.screen_size = Vector2d(500, 500)
        self.path_drawing = pygame.Surface(self.screen_size.pos)
        self.path_drawing.fill("white")
        self.screen = pygame.display.set_mode(self.screen_size.pos)
        self.gen = self.time_step()
        self.offset = Vector2d(0, 0)
        self.max_points = Vector2d(0, 0)
        # self.margin = Vector2d(50, 50)
        with open(file_path) as f:
            self.dt = float(f.readline())
            self.planets = []
            n_planets = int(f.readline())
            for _ in range(n_planets):
                planet = planet_from_str(f.readline())
                self.offset.x = min(planet.position.x, self.offset.x)
                self.max_points.x = max(planet.position.x, self.max_points.x)
                self.offset.y = min(planet.position.y, self.offset.y)
                self.max_points.y = max(planet.position.y, self.max_points.y)
                self.planets.append(planet)

            self.path: list[tuple[Vector2d, float]] = []
            while len(lines := f.readlines(LINES)) != 0:
                line = ""
                for line in lines:
                    point, angle = point_from_str(line)
                    self.offset.x = min(point.x, self.offset.x)
                    self.max_points.x = max(point.x, self.max_points.x)
                    self.offset.y = min(point.y, self.offset.y)
                    self.max_points.y = max(point.y, self.max_points.y)
                    self.path.append((point, angle))
                if line.count(" ") != 1:
                    self.rocket = rocket_from_str(line)
        x_span = self.max_points.x - self.offset.x
        y_span = self.max_points.y - self.offset.y
        self.multi = min(self.screen_size.x / x_span, self.screen_size.y / y_span)
        self.offset = Vector2d(-20, -20)
        self.multi = 5
        self.offset *= self.multi
        self.path = [(point * self.multi, angle) for point, angle in self.path]
        self.pos, self.angle = self.path[0]
        self.planets = [
            Planet(planet.position * self.multi, planet.mass, 15)
            # Planet(planet.position * self.multi, planet.mass, planet.radius * self.multi)
            for planet in self.planets
        ]
        self.rocket_surface = pygame.Surface((20, 2), pygame.SRCALPHA)
        self.rocket_surface.fill("black")
        self.draw_grid()
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
                        self.time_i = 0
                        self.step_size = len(self.path) - 10
            self.draw()
            self.clock.tick(self.FRAME_RATE)

    def save_animation(self, save_path: str, save_as_frames=False):
        """
        If save_as_frames is true, then save_path is the directory where the animation frames are saved
        """

        TIME_LIMIT = 20  # seconds
        # FPS = 60
        FPS = 24
        FRAMES = TIME_LIMIT * FPS
        images = []
        self.step_size = max(len(self.path) // FRAMES, 1)
        self.path
        self.draw()  # skip the initial, black screen
        while self.time_i < len(self.path) - 1:
            image = Image.frombytes(
                "RGB",
                (int(self.screen_size.x), int(self.screen_size.y)),
                pygame.image.tobytes(self.screen, "RGB"),
            )
            self.draw()
            images.append(image)

        print("Saving animation...")
        if not save_as_frames:
            images[0].save(save_path, save_all=True, append_images=images[1:], duration=50)
            return
        for i, image in enumerate(images):
            image.save(join(save_path, f"image-{i}.png"))

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
            n_pos, self.angle = next(self.gen)
            if high_fidelity:
                for i in range(self.time_i + 1, self.time_i + self.step_size):
                    if i == len(self.path):
                        break
                    n_pos, self.angle = self.path[i]
                    pygame.draw.line(
                        self.path_drawing,
                        self.get_color(),
                        (self.pos - self.offset).pos,
                        (n_pos - self.offset).pos,
                    )
                    self.pos = n_pos
            else:
                pygame.draw.line(
                    self.path_drawing,
                    self.get_color(),
                    (self.pos - self.offset).pos,
                    (n_pos - self.offset).pos,
                )
            self.pos: Vector2d = n_pos
        except StopIteration:
            self.gen = self.time_step()

    def draw_rocket(self):
        rotated = pygame.transform.rotate(self.rocket_surface, -self.angle * 180 / pi)
        self.screen.blit(rotated, (self.pos.x - rotated.get_rect().centerx - self.offset.x, self.pos.y - rotated.get_rect().centery - self.offset.y))

    def draw_grid(self):
        AXIS_COLOR = "black"
        MAJOR_TIC_SIZE = 10 * self.multi
        print(MAJOR_TIC_SIZE)
        MAJOR_TIC_COLOR = "#999999"

        MINOR_TIC_SIZE = 2 * self.multi
        MINOR_TIC_COLOR = "#E0E0E0"

        # hacky way of doing things
        x = -self.offset.x % MINOR_TIC_SIZE
        while x < self.screen_size.x:
            pygame.draw.line(self.path_drawing, MINOR_TIC_COLOR, (x, 0), (x, self.screen_size.y))
            x += MINOR_TIC_SIZE
        y = -self.offset.y % MINOR_TIC_SIZE
        while y < self.screen_size.y:
            pygame.draw.line(self.path_drawing, MINOR_TIC_COLOR, (0, y), (self.screen_size.x, y))
            y += MINOR_TIC_SIZE

        x = -self.offset.x % MAJOR_TIC_SIZE
        while x < self.screen_size.x:
            pygame.draw.line(self.path_drawing, MAJOR_TIC_COLOR, (x, 0), (x, self.screen_size.y))
            x += MAJOR_TIC_SIZE
        y = -self.offset.y % MAJOR_TIC_SIZE
        while y < self.screen_size.y:
            pygame.draw.line(self.path_drawing, MAJOR_TIC_COLOR, (0, y), (self.screen_size.x, y))
            y += MAJOR_TIC_SIZE

        pygame.draw.line(
            self.path_drawing, AXIS_COLOR, (-self.offset.x, 0), (-self.offset.x, self.screen_size.y)
        )
        pygame.draw.line(
            self.path_drawing, AXIS_COLOR, (0, -self.offset.y), (self.screen_size.x, -self.offset.y)
        )

    def draw(self, high_fidelity=False):
        self.draw_path(high_fidelity)
        self.screen.blit(self.path_drawing, [0, 0])
        self.draw_rocket()
        pygame.display.flip()


if __name__ == "__main__":
    v = Visualize(join("test_paths", "test3.path"))
    v.save_animation(join("animations", "test.gif"))
    # v.save_animation("animation_frames", save_as_frames=True)
    v.run()
