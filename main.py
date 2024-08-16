import pygame
import math
pygame.init()
WIDTH, HEIGHT = (800, 600)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('run in spiral OLC CodeJam 2024')
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
player_radius = 20
player_angle = 0
player_speed = 0.5
base_scale = 200
zoom_factor = 1
min_zoom = 0.25
max_zoom = 2
spiral_points = []
spiral_growth = 0.05
max_radius = math.sqrt((WIDTH / 2) ** 2 + (HEIGHT / 2) ** 2) * 0.1
running = True
clock = pygame.time.Clock()

def generate_spiral_point(angle):
    radius = math.exp(angle * spiral_growth)
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    return [x, y]
current_angle = 0
while True:
    point = generate_spiral_point(current_angle)
    if math.hypot(point[0], point[1]) > max_radius:
        break
    spiral_points.append(point)
    current_angle += 0.01

def get_player_position(angle):
    index = int(angle / 0.1)
    if index >= len(spiral_points):
        return spiral_points[-1]
    return spiral_points[index]

def get_player_orientation(angle):
    index = int(angle / 0.1)
    if index >= len(spiral_points) - 1:
        return 0
    current_point = spiral_points[index]
    next_point = spiral_points[index + 1]
    dx = next_point[0] - current_point[0]
    dy = next_point[1] - current_point[1]
    return math.atan2(dy, dx)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            zoom_factor += event.y * 0.1
            zoom_factor = max(min_zoom, min(max_zoom, zoom_factor))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player_angle > 0:
        player_angle -= player_speed
    if keys[pygame.K_d] and player_angle < (len(spiral_points) - 1) * 0.1:
        player_angle += player_speed
    player_pos = get_player_position(player_angle)
    player_orientation = get_player_orientation(player_angle)
    current_scale = base_scale * zoom_factor
    screen.fill(WHITE)
    if len(spiral_points) > 1:
        adjusted_points = []
        for point in spiral_points:
            offset_x = point[0] - player_pos[0]
            offset_y = point[1] - player_pos[1]
            rotated_x = offset_x * math.cos(-player_orientation) - offset_y * math.sin(-player_orientation)
            rotated_y = offset_x * math.sin(-player_orientation) + offset_y * math.cos(-player_orientation)
            screen_x = rotated_x * current_scale + WIDTH // 2
            screen_y = rotated_y * current_scale + HEIGHT // 2
            adjusted_points.append((screen_x, screen_y))
        pygame.draw.lines(screen, BLACK, False, adjusted_points, 2)
    player_screen_pos = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.circle(screen, RED, player_screen_pos, player_radius)
    line_end = (player_screen_pos[0], player_screen_pos[1] - player_radius)
    pygame.draw.line(screen, BLACK, player_screen_pos, line_end, 2)
    if player_angle >= (len(spiral_points) - 1) * 0.1:
        font = pygame.font.Font(None, 36)
        win_text = font.render("You've reached the end of the spiral!", True, BLACK)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()