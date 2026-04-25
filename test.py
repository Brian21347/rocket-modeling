import pygame
import sys


pygame.init()
rocket_surface = pygame.Surface((100, 10), pygame.SRCALPHA)
rocket_surface.fill("black")
angle = 0
clock = pygame.time.Clock()


screen = pygame.display.set_mode([500, 500])
dangle = 0.1


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                dangle += 0.1
            if event.key == pygame.K_DOWN:
                dangle -= 0.1
    screen.fill("white")
    rotated = pygame.transform.rotate(rocket_surface, angle)
    screen.blit(rotated, (100 - rotated.get_rect().centerx, 100 - rotated.get_rect().centery))
    pygame.display.update()
    angle += dangle
    clock.tick(10)
    print(angle)
