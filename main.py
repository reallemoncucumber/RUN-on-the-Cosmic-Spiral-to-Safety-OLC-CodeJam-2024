import pygame
import math
import random
import colorsys
pygame.init()
WIDTH, HEIGHT = (800, 600)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Run in Spiral OLC CodeJam 2024')
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 250, 205)
base_speed = 1
base_scale = 1
zoom_factor = 1
min_zoom = 0.25
max_zoom = 2
spiral_points = []
max_distance = math.sqrt((WIDTH / 2) ** 2 + (HEIGHT / 2) ** 2) * 10
running = True
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
original_astronaut_sprites = [pygame.image.load(f'assets\\images\\astro\\astro-{i}.png') for i in range(1, 6)]
meteorite_sprite = pygame.image.load('assets\\images\\meteorite.png')
base_meteorite_scale = 0.5
scaled_meteorite_sprite = pygame.transform.scale(meteorite_sprite, (int(meteorite_sprite.get_width() * base_meteorite_scale), int(meteorite_sprite.get_height() * base_meteorite_scale)))
base_sprite_scale = 0.1
astronaut_sprites = []
current_sprite = 0
sprite_update_time = 0
sprite_update_delay = 100
facing_right = True
a = 50
b = 0.1
rainbow_repetitions = 5

class Meteorite:

    def __init__(self):
        self.x = WIDTH + random.randint(0, 200)
        self.y = random.randint(-200, 0)
        self.speed = random.uniform(2, 5)
        self.angle = math.radians(random.uniform(150, 200))

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def is_off_screen(self):
        return self.x < -1000 or self.y > HEIGHT + 1000
meteorites = []
meteorite_spawn_timer = 0
meteorite_spawn_interval = 2000

def scale_meteorite_sprite(zoom):
    global scaled_meteorite_sprite
    current_scale = base_meteorite_scale * zoom
    scaled_meteorite_sprite = pygame.transform.scale(meteorite_sprite, (int(meteorite_sprite.get_width() * current_scale), int(meteorite_sprite.get_height() * current_scale)))

def scale_sprites(zoom):
    global astronaut_sprites
    current_scale = base_sprite_scale * zoom
    astronaut_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * current_scale), int(sprite.get_height() * current_scale))) for sprite in original_astronaut_sprites]
scale_sprites(zoom_factor)

def generate_spiral_points():
    t = 0
    while True:
        r = a * math.exp(b * t)
        x = r * math.cos(t)
        y = r * math.sin(t)
        if math.hypot(x, y) > max_distance:
            break
        spiral_points.append((x, y))
        t += 0.05
generate_spiral_points()
player_index = 0
player_pos = spiral_points[player_index]

def get_rainbow_color(t):
    """
    Generate a rainbow color based on a value t between 0 and 1.
    """
    r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)

def get_player_speed(index):
    return base_speed

def get_player_orientation():
    if player_index >= len(spiral_points) - 1:
        return 0
    current_point = spiral_points[int(player_index)]
    next_point = spiral_points[int(player_index + 1)]
    dx = next_point[0] - current_point[0]
    dy = next_point[1] - current_point[1]
    return math.atan2(dy, dx)

def create_star():
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(1, 2)
    return (x, y, radius)

def create_nebula():
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(50, 150)
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    return (x, y, radius, color)

def create_planet():
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(20, 60)
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    return (x, y, radius, color)

def create_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)
    nebulae = [create_nebula() for _ in range(3)]
    stars = [create_star() for _ in range(200)]
    planets = [create_planet() for _ in range(5)]
    for nebula in nebulae:
        pygame.draw.circle(background, nebula[3], (nebula[0], nebula[1]), nebula[2])
    for star in stars:
        pygame.draw.circle(background, WHITE, (star[0], star[1]), star[2])
    for planet in planets:
        pygame.draw.circle(background, planet[3], (planet[0], planet[1]), planet[2])
    return background

def blend_surfaces(surface1, surface2, alpha):
    result = surface1.copy()
    surface2.set_alpha(int(alpha * 255))
    result.blit(surface2, (0, 0))
    return result
num_backgrounds = 5
backgrounds = [create_background() for _ in range(num_backgrounds)]
current_background_index = 0
next_background_index = 1
transition_progress = 0
transition_speed = 0.002
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEWHEEL:
            zoom_factor += event.y * 0.1
            zoom_factor = max(min_zoom, min(max_zoom, zoom_factor))
            scale_sprites(zoom_factor)
            scale_meteorite_sprite(zoom_factor)
    keys = pygame.key.get_pressed()
    moving = False
    current_time = pygame.time.get_ticks()
    current_speed = get_player_speed(player_index)
    if current_time - meteorite_spawn_timer > meteorite_spawn_interval:
        meteorites.append(Meteorite())
        meteorite_spawn_timer = current_time
    for meteorite in meteorites[:]:
        meteorite.move()
        if meteorite.is_off_screen():
            meteorites.remove(meteorite)
    if keys[pygame.K_a] and player_index > 0:
        player_index = max(0, player_index - current_speed)
        player_pos = spiral_points[int(player_index)]
        transition_progress -= transition_speed * current_speed
        moving = True
        facing_right = False
    if keys[pygame.K_d] and player_index < len(spiral_points) - 1:
        player_index = min(len(spiral_points) - 1, player_index + current_speed)
        player_pos = spiral_points[int(player_index)]
        transition_progress += transition_speed * current_speed
        moving = True
        facing_right = True
    if transition_progress >= 1:
        current_background_index = next_background_index
        next_background_index = (next_background_index + 1) % num_backgrounds
        transition_progress = 0
    elif transition_progress < 0:
        next_background_index = current_background_index
        current_background_index = (current_background_index - 1) % num_backgrounds
        transition_progress = 1 + transition_progress
    transition_progress = max(0, min(1, transition_progress))
    player_orientation = get_player_orientation()
    current_scale = base_scale * zoom_factor
    current_bg = backgrounds[current_background_index]
    next_bg = backgrounds[next_background_index]
    blended_background = blend_surfaces(current_bg, next_bg, transition_progress)
    screen.blit(blended_background, (0, 0))
    if len(spiral_points) > 1:
        adjusted_points = []
        for i, point in enumerate(spiral_points):
            offset_x = point[0] - player_pos[0]
            offset_y = point[1] - player_pos[1]
            rotated_x = offset_x * math.cos(-player_orientation) - offset_y * math.sin(-player_orientation)
            rotated_y = offset_x * math.sin(-player_orientation) + offset_y * math.cos(-player_orientation)
            screen_x = rotated_x * current_scale * base_scale + WIDTH // 2
            screen_y = rotated_y * current_scale * base_scale + HEIGHT // 2
            adjusted_points.append((screen_x, screen_y))
        
        for i in range(len(adjusted_points) - 1):
            start_point = adjusted_points[i]
            end_point = adjusted_points[i + 1]
            t = (i / len(adjusted_points)) * rainbow_repetitions  # Multiply by rainbow_repetitions
            t = t - int(t)  # This operation keeps t between 0 and 1
            color = get_rainbow_color(t)
            pygame.draw.line(screen, color, start_point, end_point, 2)
    player_screen_pos = (WIDTH // 2, HEIGHT // 2)
    if moving:
        if current_time - sprite_update_time > sprite_update_delay:
            current_sprite = (current_sprite + 1) % 5
            sprite_update_time = current_time
    else:
        current_sprite = 0
    sprite = astronaut_sprites[current_sprite]
    if not facing_right:
        sprite = pygame.transform.flip(sprite, True, False)
    base_offset = 12
    zoom_adjusted_offset = base_offset * zoom_factor
    sprite_offset_y = sprite.get_height() // 2 - zoom_adjusted_offset
    sprite_pos = (player_screen_pos[0], player_screen_pos[1] - sprite_offset_y)
    sprite_rect = sprite.get_rect(midbottom=sprite_pos)
    screen.blit(sprite, sprite_rect)
    for meteorite in meteorites:
        offset_x = meteorite.x - player_pos[0]
        offset_y = meteorite.y - player_pos[1]
        rotated_x = offset_x * math.cos(-player_orientation) - offset_y * math.sin(-player_orientation)
        rotated_y = offset_x * math.sin(-player_orientation) + offset_y * math.cos(-player_orientation)
        screen_x = rotated_x * current_scale * base_scale + WIDTH // 2
        screen_y = rotated_y * current_scale * base_scale + HEIGHT // 2
        meteorite_rect = scaled_meteorite_sprite.get_rect(center=(screen_x, screen_y))
        screen.blit(scaled_meteorite_sprite, meteorite_rect)
    if player_index == len(spiral_points) - 1:
        win_text = font.render("You've reached the end of the spiral!", True, WHITE)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()