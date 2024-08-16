import pygame
import math
pygame.init()
width, height = (800, 600)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('run in spiral OLC CodeJam 2024')
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
a = 0
b = 0.3
num_points = 1000
spiral_points = []
for i in range(num_points):
    theta = i * 50
    r = a + b * theta
    x = int(width / 2 + r * math.cos(theta))
    y = int(height / 2 + r * math.sin(theta))
    spiral_points.append((x, y))
rect_width, rect_height = (20, 20)
rect_pos = 0
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        rect_pos = max(0, rect_pos - 1)
    if keys[pygame.K_d]:
        rect_pos = min(len(spiral_points) - 1, rect_pos + 1)
    screen.fill(BLACK)
    pygame.draw.lines(screen, WHITE, False, spiral_points, 2)
    rect_x, rect_y = spiral_points[rect_pos]
    pygame.draw.rect(screen, RED, (rect_x - rect_width // 2, rect_y - rect_height // 2, rect_width, rect_height))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()