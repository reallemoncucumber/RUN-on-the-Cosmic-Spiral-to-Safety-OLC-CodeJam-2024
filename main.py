import asyncio
import pygame
import math
import random
import colorsys
import sys
if sys.platform == 'emscripten':
    platform.window.canvas.style.imageRendering = 'pixelated'
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.music.load('assets/sounds/soundtrack.ogg')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)
WIDTH, HEIGHT = (800, 600)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Run in Spiral OLC CodeJam 2024')
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 250, 205)
CYAN = (0, 255, 255)
GREEN = (144, 238, 144)
base_speed = 1
base_scale = 1
zoom_factor = 1
min_zoom = 1
max_zoom = 1
max_distance = math.sqrt((WIDTH / 2) ** 2 + (HEIGHT / 2) ** 2) * 10
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
original_astronaut_sprites = [pygame.image.load(f'assets/images/astro/astro-{i}.png') for i in range(1, 6)]
meteorite_sprite = pygame.image.load('assets/images/meteorite.png')
space_shuttle_sprite = pygame.image.load('assets/images/space_shuttle.png')
base_shuttle_scale = 0.2
base_meteorite_scale = 0.2
scaled_meteorite_sprite = pygame.transform.scale(meteorite_sprite, (int(meteorite_sprite.get_width() * base_meteorite_scale), int(meteorite_sprite.get_height() * base_meteorite_scale)))
scaled_shuttle_sprite = pygame.transform.scale(space_shuttle_sprite, (int(space_shuttle_sprite.get_width() * base_shuttle_scale), int(space_shuttle_sprite.get_height() * base_shuttle_scale)))
base_sprite_scale = 0.1
astronaut_sprites = []
current_sprite = 0
sprite_update_time = 0
sprite_update_delay = 100
facing_right = True
a = 50
b = 0.1
rainbow_repetitions = 5
game_over_rotation = 0
game_over_scale = 1
max_game_over_scale = 20
game_over_scale_speed = 0.1
game_over_rotation_speed = 5
star_speed = 1
game_won = False
background_change_timer = 0
background_change_interval = 2000
start_screen_sprite = pygame.image.load('assets/images/start_screen.png')
font_size = 52
stamina_font_size = 28
font = pygame.font.Font(None, font_size)
font_hud = pygame.font.Font(None, stamina_font_size)

def check_win_condition(player_rect, shuttle_rect):
    return player_rect.colliderect(shuttle_rect)

def create_pixelated_text(text, font, font_size):
    temp_font = pygame.font.Font(None, font_size * 8)
    text_surface = font.render(text, True, WHITE)
    temp_text_surface = temp_font.render(text, True, WHITE)
    small_surface = pygame.transform.scale(temp_text_surface, (temp_text_surface.get_width() // 20, temp_text_surface.get_height() // 20))
    pixelated_surface = pygame.transform.scale(small_surface, (text_surface.get_width(), text_surface.get_height()))
    return pixelated_surface

def start_menu_logic(screen, pixelated_text, button, time, bounce_speed, bounce_height):
    offset = math.sin(time * bounce_speed) * bounce_height
    screen.blit(start_screen_sprite, (0, 0))
    text_width = pixelated_text.get_width()
    text_pos = ((WIDTH - text_width) // 2, HEIGHT // 4 + offset)
    screen.blit(pixelated_text, text_pos)
    mouse_pos = pygame.mouse.get_pos()
    button_color = button['hover_color'] if button['rect'].collidepoint(mouse_pos) else button['color']
    pygame.draw.rect(screen, button_color, button['rect'])
    screen.blit(button['text'], button['text_rect'])

def create_button(text, font, width, height, pos, color, hover_color):
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    button_rect = pygame.Rect(pos[0], pos[1], width, height)
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=button_rect.center)
    return {'surface': button_surface, 'rect': button_rect, 'text': text_surf, 'text_rect': text_rect, 'color': color, 'hover_color': hover_color}

def circles_intersect(x1, y1, r1, x2, y2, r2):
    """Check if two circles intersect."""
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance <= r1 + r2

class MeteoriteSquare:

    def __init__(self, player_pos):
        self.player_x, self.player_y = player_pos
        self.size = 1200
        self.buffer = 200
        self.x = self.player_x - self.size // 2
        self.y = self.player_y - self.size // 2
        self.spawn_positions = [(self.x - 100, self.player_y - 100), (self.x + self.size + 100, self.player_y + 100)]
        self.spawn_angle_range = (math.pi, 3 * math.pi / 2)
        self.previous_quarter = -1
        self.repulsion_active = False
        self.repulsion_radius = 0
        self.max_repulsion_radius = 200
        self.repulsion_speed = 5

    def update(self, player_pos):
        self.player_x, self.player_y = player_pos
        self.x = self.player_x - self.size // 2
        self.y = self.player_y - self.size // 2
        self.spawn_positions = [(self.x - 100, self.player_y - 100), (self.x + self.size + 100, self.player_y + 100)]
        if self.repulsion_active:
            self.repulsion_radius += self.repulsion_speed
            if self.repulsion_radius > self.max_repulsion_radius:
                self.repulsion_active = False
                self.repulsion_radius = 0

    def activate_repulsion_field(self):
        self.repulsion_active = True
        self.repulsion_radius = 0

    def apply_repulsion(self, meteorites):
        if not self.repulsion_active:
            return
        for meteorite in meteorites:
            distance = math.sqrt((meteorite.x - self.player_x) ** 2 + (meteorite.y - self.player_y) ** 2)
            meteorite_radius = max(scaled_meteorite_sprite.get_width(), scaled_meteorite_sprite.get_height()) * meteorite.scale_factor / 2
            deplayed_effect_offset = 20
            if self.repulsion_radius - deplayed_effect_offset >= distance - meteorite_radius:
                angle_to_player = math.atan2(meteorite.y - self.player_y, meteorite.x - self.player_x)
                meteorite.repulse(angle_to_player)

    def spawn_meteorites(self, player_progress):
        meteorites = []
        current_quarter = int(player_progress * 4)
        for _ in range(current_quarter - self.previous_quarter):
            spawn_pos = random.choice(self.spawn_positions)
            angle = random.uniform(self.spawn_angle_range[0], self.spawn_angle_range[1])
            meteorites.append(Meteorite(spawn_pos, angle, player_progress))
        self.previous_quarter = current_quarter
        return meteorites

class Meteorite:

    def __init__(self, pos, angle, player_progress):
        self.x, self.y = pos
        self.angle = angle
        self.scale_factor = random.uniform(0.2, 2)
        self.speed = random.uniform(2, 5)
        progress_factor = 1 - player_progress
        progress_factor = min(progress_factor, 0.5)
        angle_offset = math.pi / 4 * progress_factor
        self.angle += random.uniform(-angle_offset, angle_offset)
        self.mask = pygame.mask.from_surface(pygame.transform.scale(scaled_meteorite_sprite, (int(scaled_meteorite_sprite.get_width() * self.scale_factor), int(scaled_meteorite_sprite.get_height() * self.scale_factor))))

    def move(self, square_x, square_y, square_size, buffer):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        if self.x < square_x - buffer or self.x > square_x + square_size + buffer or self.y < square_y - buffer or (self.y > square_y + square_size + buffer):
            if self.off_screen:
                if self.x < square_x - buffer:
                    self.x = square_x + square_size + buffer
                elif self.x > square_x + square_size + buffer:
                    self.x = square_x - buffer
                if self.y < square_y - buffer:
                    self.y = square_y + square_size + buffer
                elif self.y > square_y + square_size + buffer:
                    self.y = square_y - buffer
                center_x = square_x + square_size / 2
                center_y = square_y + square_size / 2
                self.angle = math.atan2(center_y - self.y, center_x - self.x)
                self.off_screen = False
            else:
                self.off_screen = True
        else:
            self.off_screen = False

    def repulse(self, angle_from_player):
        if self.repulsed:
            return
        self.angle %= 2 * math.pi
        self.angle = angle_from_player
        self.angle %= 2 * math.pi
        self.repulsed = True
meteorites = []
meteorite_spawn_timer = 0

def scale_meteorite_sprite(zoom):
    global scaled_meteorite_sprite
    current_scale = base_meteorite_scale * zoom
    scaled_meteorite_sprite = pygame.transform.scale(meteorite_sprite, (int(meteorite_sprite.get_width() * current_scale), int(meteorite_sprite.get_height() * current_scale)))
    for meteorite in meteorites:
        meteorite.mask = pygame.mask.from_surface(scaled_meteorite_sprite)

def scale_sprites(zoom):
    global astronaut_sprites
    current_scale = base_sprite_scale * zoom
    astronaut_sprites = [pygame.transform.scale(sprite, (int(sprite.get_width() * current_scale), int(sprite.get_height() * current_scale))) for sprite in original_astronaut_sprites]
scale_sprites(zoom_factor)

def generate_spiral_points():
    from collections import defaultdict
    initial_step = 0.01
    max_step = 0.003
    decay_factor = 0.999845
    spiral_points = []
    t = 0
    step = initial_step
    d = defaultdict(int)
    while True:
        r = a * math.exp(b * t)
        x = r * math.cos(t)
        y = r * math.sin(t)
        if math.hypot(x, y) > max_distance:
            break
        spiral_points.append((x, y))
        step *= decay_factor
        step = max(step, max_step)
        d[step] += 1
        t += step
    return spiral_points
player_index = 0
spiral_points = generate_spiral_points()
player_pos = spiral_points[player_index]

def get_rainbow_color(t):
    r, g, b = colorsys.hsv_to_rgb(t, 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))

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
    return [x, y, radius]
stars = [create_star() for _ in range(200)]

def move_stars():
    for star in stars:
        star[0] -= star_speed
        if star[0] < 0:
            star[0] = WIDTH
            star[1] = random.randint(0, HEIGHT)

def is_point_inside_circle(x, y, circle_x, circle_y, radius):
    distance = math.sqrt((x - circle_x) ** 2 + (y - circle_y) ** 2)
    return distance <= radius

def is_star_visible(star, planets1, nebulae1, planets2, nebulae2, blend_factor, game_won):
    if game_won:
        return True
    for planet in planets1:
        if is_point_inside_circle(star[0], star[1], planet[0], planet[1], planet[2] * blend_factor):
            return False
    for nebula in nebulae1:
        if is_point_inside_circle(star[0], star[1], nebula[0], nebula[1], nebula[2] * blend_factor):
            return False
    for planet in planets2:
        if is_point_inside_circle(star[0], star[1], planet[0], planet[1], planet[2] * blend_factor):
            return False
    for nebula in nebulae2:
        if is_point_inside_circle(star[0], star[1], nebula[0], nebula[1], nebula[2] * blend_factor):
            return False
    return True

def draw_stars(surface, stars, planets1, nebulae1, planets2, nebulae2, blend_factor, game_won):
    for star in stars:
        if is_star_visible(star, planets1, nebulae1, planets2, nebulae2, blend_factor, game_won):
            pygame.draw.circle(surface, WHITE, (int(star[0]), int(star[1])), star[2])

def create_planet():
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(20, 60)
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    return (x, y, radius, color)

def create_nebula():
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(50, 150)
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    return (x, y, radius, color)

def create_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)
    nebulae = [create_nebula() for _ in range(3)]
    planets = [create_planet() for _ in range(5)]
    for nebula in nebulae:
        pygame.draw.circle(background, nebula[3], (nebula[0], nebula[1]), nebula[2])
    for planet in planets:
        pygame.draw.circle(background, planet[3], (planet[0], planet[1]), planet[2])
    return (background, planets, nebulae)

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

class Crack:

    def __init__(self, x, y, angle, depth=0, length=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.length = length
        self.children = []
        self.growing = True
        self.max_length = random.randint(30, 70)
        self.depth = depth

    def grow(self):
        if not self.growing:
            return
        self.length += random.randint(10, 25)
        if self.length >= self.max_length:
            self.growing = False
            self.branch()

    def branch(self):
        if len(self.children) > 0:
            return
        branch_probability = max(0.1, 0.7 - self.depth * 0.1)
        if random.random() > branch_probability:
            return
        num_branches = random.randint(1, 3)
        for _ in range(num_branches):
            angle_change = random.uniform(-math.pi / 4, math.pi / 4)
            new_angle = self.angle + angle_change
            end_x = self.x + self.length * math.cos(self.angle)
            end_y = self.y + self.length * math.sin(self.angle)
            self.children.append(Crack(end_x, end_y, new_angle, self.depth + 1))

    def draw(self, surface):
        end_x = self.x + self.length * math.cos(self.angle)
        end_y = self.y + self.length * math.sin(self.angle)
        pygame.draw.line(surface, CYAN, (self.x, self.y), (end_x, end_y), 3)
        for child in self.children:
            child.draw(surface)

    def update(self):
        self.grow()
        for child in self.children:
            child.update()
num_initial_cracks = 10
cracks = [Crack(WIDTH // 2, HEIGHT // 2, random.uniform(0, 2 * math.pi)) for _ in range(num_initial_cracks)]
screen_shake_duration = 0
screen_shake_intensity = 10
SPRINT_SPEED_MULTIPLIER = 3
SPRINT_STAMINA_CONSUMPTION = 1
SPRINT_STAMINA_REGENERATION = 0.1

class Player:

    def __init__(self):
        self.stamina = 100.0
        self.is_sprinting = False
        self.repulsion_charges = 10

    def update(self, keys, current_speed):
        self.stamina = min(100.0, self.stamina + SPRINT_STAMINA_REGENERATION)
        if keys[pygame.K_w] and (keys[pygame.K_d] or keys[pygame.K_a]):
            self.is_sprinting = True
            self.stamina = max(0.0, self.stamina - SPRINT_STAMINA_CONSUMPTION)
        else:
            self.is_sprinting = False
        if self.is_sprinting and self.stamina > 0:
            return current_speed * SPRINT_SPEED_MULTIPLIER
        else:
            return current_speed

    def use_repulsion_charge(self):
        if self.repulsion_charges > 0:
            self.repulsion_charges -= 1
            return True
        return False
player = Player()

def apply_screen_shake(surface):
    global screen_shake_duration
    if screen_shake_duration > 0:
        shake_offset = (random.randint(-screen_shake_intensity, screen_shake_intensity), random.randint(-screen_shake_intensity, screen_shake_intensity))
        screen.blit(surface, shake_offset)
        screen_shake_duration -= 1
        if screen_shake_duration == 0:
            screen_shake_duration = -1
    else:
        screen.blit(surface, (0, 0))

def reset_game():
    global player_index, player_pos, meteorites, current_background_index, next_background_index, transition_progress, game_over_rotation, game_over_scale, screen_shake_duration, game_over, player, meteorite_square, game_won
    player_index = 0
    player_pos = spiral_points[player_index]
    meteorites.clear()
    meteorite_square = MeteoriteSquare(player_pos)
    current_background_index = 0
    next_background_index = 1
    transition_progress = 0
    game_over_rotation = 0
    game_over_scale = 1
    screen_shake_duration = 0
    game_over = False
    game_won = False
    player = Player()

def check_collision(player_rect, player_mask, meteorite_rect, meteorite_mask):
    offset = (meteorite_rect.x - player_rect.x, meteorite_rect.y - player_rect.y)
    return player_mask.overlap(meteorite_mask, offset)
moving = False
running = True
game_over = False
try_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
sprite_rect = None
meteorite_square = None

async def run_game():
    global player_index, player_pos, meteorites, current_background_index, next_background_index, transition_progress, game_over_rotation, game_over_scale, screen_shake_duration, running, game_over, game_won, zoom_factor
    global moving, facing_right, meteorite_spawn_timer, sprite_rect, sprite_update_time, background_change_timer, sprite, meteorite_square
    music_volume = 0.3
    pygame.mixer.music.set_volume(music_volume)
    mute_button = create_button('Mute', font_hud, 100, 30, (20, 20), (128, 128, 128), (150, 150, 150))
    reset_button = create_button('Reset', font_hud, 100, 30, (20, 60), (128, 128, 128), (150, 150, 150))
    is_muted = False
    player_index = 0
    player_pos = spiral_points[player_index]
    meteorites = []
    player_progress = 0
    meteorite_square = MeteoriteSquare(player_pos)
    current_background_index = 0
    next_background_index = 1
    transition_progress = 0
    game_over_rotation = 0
    game_over_scale = 1
    screen_shake_duration = 0
    running = True
    game_over = False
    game_won = False
    title_text = 'RUN on the Cosmic Spiral to Safety!'
    pixelated_text = create_pixelated_text(title_text, font, font_size)
    start_button = create_button('Start Game', font, 200, 50, (WIDTH // 2 - 100, HEIGHT * 3 // 4), (100, 100, 100), (150, 150, 150))
    game_state = 'START_MENU'
    clock = pygame.time.Clock()
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if player.use_repulsion_charge():
                        meteorite_square.activate_repulsion_field()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == 'START_MENU' and start_button['rect'].collidepoint(event.pos):
                    game_state = 'GAME'
                elif game_state == 'GAME_OVER' and try_again_button.collidepoint(event.pos):
                    reset_game()
                    game_state = 'GAME'
                if mute_button['rect'].collidepoint(event.pos):
                    is_muted = not is_muted
                    if is_muted:
                        pygame.mixer.music.set_volume(0)
                        mute_button['text'] = font_hud.render('Unmute', True, (255, 255, 255))
                    else:
                        pygame.mixer.music.set_volume(music_volume)
                        mute_button['text'] = font_hud.render('Mute', True, (255, 255, 255))
                if reset_button['rect'].collidepoint(event.pos):
                    reset_game()
                    game_state = 'GAME'
            elif event.type == pygame.MOUSEWHEEL and game_state == 'GAME':
                zoom_factor += event.y * 0.1
                zoom_factor = max(min_zoom, min(max_zoom, zoom_factor))
                scale_sprites(zoom_factor)
                scale_meteorite_sprite(zoom_factor)
        player_orientation = get_player_orientation()
        current_scale = base_scale * zoom_factor
        if game_state == 'START_MENU':
            start_menu_logic(screen, pixelated_text, start_button, current_time / 1000, 2, 20)
        elif game_state == 'GAME':
            keys = pygame.key.get_pressed()
            moving = False
            current_time = pygame.time.get_ticks()
            keys = pygame.key.get_pressed()
            current_speed = get_player_speed(player_index)
            player_speed = player.update(keys, current_speed)
            player_progress = player_index / (len(spiral_points) - 1)
            meteorite_check_interval = 1000
            meteorite_square.update(player_pos)
            if current_time - meteorite_spawn_timer > meteorite_check_interval:
                meteorite_spawn_timer = current_time
                new_meteorites = meteorite_square.spawn_meteorites(player_progress)
                meteorites.extend(new_meteorites)
            meteorite_square.apply_repulsion(meteorites)
            for meteorite in meteorites:
                meteorite.move(meteorite_square.x, meteorite_square.y, meteorite_square.size, meteorite_square.buffer)
            if not meteorite_square.repulsion_active:
                for meteorite in meteorites:
                    meteorite.repulsed = False
            if not game_won:
                if keys[pygame.K_a] and player_index > 0:
                    player_index = max(0, player_index - player_speed)
                    player_pos = spiral_points[int(player_index)]
                    transition_progress -= transition_speed * player_speed
                    moving = True
                    facing_right = False
                elif keys[pygame.K_d] and player_index < len(spiral_points) - 1:
                    player_index = min(len(spiral_points) - 1, player_index + player_speed)
                    player_pos = spiral_points[int(player_index)]
                    transition_progress += transition_speed * player_speed
                    moving = True
                    facing_right = True
                else:
                    moving = False
            if transition_progress >= 1:
                current_background_index = next_background_index
                next_background_index = (next_background_index + 1) % num_backgrounds
                transition_progress = 0
            elif transition_progress < 0:
                next_background_index = current_background_index
                current_background_index = (current_background_index - 1) % num_backgrounds
                transition_progress = 1 + transition_progress
            transition_progress = max(0, min(1, transition_progress))
            if game_over:
                game_state = 'GAME_OVER'
            elif game_won:
                game_state = 'GAME_WON'
        elif game_state == 'GAME_WON':
            transition_progress = 0
            move_stars()
            if current_time - background_change_timer > background_change_interval:
                current_background_index = (current_background_index + 1) % num_backgrounds
                background_change_timer = current_time
        if game_state != 'START_MENU':
            current_bg, current_planets, current_nebulae = backgrounds[current_background_index]
            next_bg, next_planets, next_nebulae = backgrounds[next_background_index]
            blended_background = blend_surfaces(current_bg, next_bg, transition_progress)
            game_surface = pygame.Surface((WIDTH, HEIGHT))
            if not game_won:
                game_surface.blit(blended_background, (0, 0))
            if game_won:
                transition_progress = 0
                blend_factor = 1
            else:
                blend_factor = 1
            draw_stars(game_surface, stars, current_planets, current_nebulae, next_planets, next_nebulae, blend_factor, game_won)
            if not game_won:
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
                        t = i / len(adjusted_points) * rainbow_repetitions
                        t = t - int(t)
                        color = get_rainbow_color(t)
                        pygame.draw.line(game_surface, color, start_point, end_point, 2)
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
                for meteorite in meteorites:
                    offset_x = meteorite.x - player_pos[0]
                    offset_y = meteorite.y - player_pos[1]
                    rotated_x = offset_x * math.cos(-player_orientation) - offset_y * math.sin(-player_orientation)
                    rotated_y = offset_x * math.sin(-player_orientation) + offset_y * math.cos(-player_orientation)
                    screen_x = rotated_x * current_scale * base_scale + WIDTH // 2
                    screen_y = rotated_y * current_scale * base_scale + HEIGHT // 2
                    meteorite_rect = pygame.transform.scale(scaled_meteorite_sprite, (int(scaled_meteorite_sprite.get_width() * meteorite.scale_factor), int(scaled_meteorite_sprite.get_height() * meteorite.scale_factor))).get_rect(center=(screen_x, screen_y))
                    game_surface.blit(pygame.transform.scale(scaled_meteorite_sprite, (int(scaled_meteorite_sprite.get_width() * meteorite.scale_factor), int(scaled_meteorite_sprite.get_height() * meteorite.scale_factor))), meteorite_rect)
                    if sprite_rect is not None and sprite_rect.inflate(200, 200).colliderect(meteorite_rect):
                        if sprite_rect is not None and check_collision(sprite_rect, player_mask, meteorite_rect, meteorite.mask):
                            game_over = True
            if meteorite_square.repulsion_active:
                repulsion_center = sprite_rect.center
                pygame.draw.circle(game_surface, (0, 255, 255), repulsion_center, int(meteorite_square.repulsion_radius), 2)
            if game_over:
                current_sprite = 0
                game_over_rotation += game_over_rotation_speed
                game_over_scale = min(game_over_scale + game_over_scale_speed, max_game_over_scale)
                if game_over_scale < max_game_over_scale:
                    rotated_sprite = pygame.transform.rotate(sprite, game_over_rotation)
                scaled_sprite = pygame.transform.scale(rotated_sprite, (int(rotated_sprite.get_width() * game_over_scale), int(rotated_sprite.get_height() * game_over_scale)))
                sprite_rect = scaled_sprite.get_rect(center=player_screen_pos)
                game_surface.blit(scaled_sprite, sprite_rect)
            else:
                base_offset = 12
                zoom_adjusted_offset = base_offset * zoom_factor
                sprite_offset_y = sprite.get_height() // 2 - zoom_adjusted_offset
                sprite_pos = (player_screen_pos[0], player_screen_pos[1] - sprite_offset_y)
                sprite_rect = sprite.get_rect(midbottom=sprite_pos)
                game_surface.blit(sprite, sprite_rect)
            player_mask = pygame.mask.from_surface(sprite)
            last_point = spiral_points[-1]
            offset_x = last_point[0] - player_pos[0]
            offset_y = last_point[1] - player_pos[1]
            rotated_x = offset_x * math.cos(-player_orientation) - offset_y * math.sin(-player_orientation)
            rotated_y = offset_x * math.sin(-player_orientation) + offset_y * math.cos(-player_orientation)
            shuttle_x = rotated_x * current_scale * base_scale + WIDTH // 2
            shuttle_y = rotated_y * current_scale * base_scale + HEIGHT // 2
            shuttle_rect = scaled_shuttle_sprite.get_rect(center=(shuttle_x, shuttle_y))
            game_surface.blit(scaled_shuttle_sprite, shuttle_rect)
            if player_index >= len(spiral_points) - 6:
                game_won = True
                player_pos = spiral_points[len(spiral_points) - 1]
                win_text = font.render('You won!', True, GREEN)
                game_surface.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 4))
            if game_over:
                if game_over_scale >= max_game_over_scale:
                    if screen_shake_duration == 0:
                        screen_shake_duration = 30
                    for crack in cracks:
                        crack.update()
                        crack.draw(game_surface)
                    game_over_text = font.render('Game Over!', True, RED)
                    game_surface.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
                    pygame.draw.rect(game_surface, YELLOW, try_again_button)
                    try_again_text = font.render('Try Again', True, BLACK)
                    game_surface.blit(try_again_text, (try_again_button.x + try_again_button.width // 2 - try_again_text.get_width() // 2, try_again_button.y + try_again_button.height // 2 - try_again_text.get_height() // 2))
            if not game_won:
                stamina_bar_width = 200
                stamina_bar_height = 20
                stamina_bar_x = WIDTH - stamina_bar_width - 20
                stamina_bar_y = HEIGHT - stamina_bar_height - 20
                stamina_bar_rect = pygame.Rect(stamina_bar_x, stamina_bar_y, stamina_bar_width, stamina_bar_height)
                stamina_percent = player.stamina / 100.0
                stamina_bar_color = (0, 255, 0)
                stamina_bar_active_width = int(stamina_bar_width * stamina_percent)
                stamina_bar_active_rect = pygame.Rect(stamina_bar_x, stamina_bar_y, stamina_bar_active_width, stamina_bar_height)
                pygame.draw.rect(game_surface, (128, 128, 128), stamina_bar_rect)
                pygame.draw.rect(game_surface, stamina_bar_color, stamina_bar_active_rect)
                pygame.draw.rect(game_surface, (255, 255, 255), stamina_bar_rect, 2)
                stamina_text = font_hud.render('Stamina', True, (255, 255, 255))
                stamina_text_rect = pygame.Rect(stamina_bar_x, stamina_bar_y - 30, stamina_bar_active_width, stamina_bar_height)
                game_surface.blit(stamina_text, stamina_text_rect)
                charge_text = font_hud.render(f'Repellant Charges: {player.repulsion_charges}', True, (255, 255, 255))
                charge_text_rect = tamina_text_rect = pygame.Rect(stamina_bar_x, stamina_bar_y - 60, stamina_bar_active_width, stamina_bar_height)
                game_surface.blit(charge_text, charge_text_rect)
                stamina_text = font_hud.render(f'{int(player.stamina)}%', True, (0, 0, 0))
                stamina_text_rect = stamina_text.get_rect(center=(stamina_bar_x + stamina_bar_width // 2, stamina_bar_y + stamina_bar_height // 2))
                game_surface.blit(stamina_text, stamina_text_rect)
                progress_text = font_hud.render(f'Progress: {int(player_index / (len(spiral_points) - 1) * 100)}%', True, (255, 255, 255))
                progress_text_rect = progress_text.get_rect(topright=(WIDTH - 20, 20))
                game_surface.blit(progress_text, progress_text_rect)
                controls_text = ['Controls:', 'A/D (move left/right)', 'W (sprint)', 'S (meteorite repellant)']
                controls_text_color = (255, 255, 255)
                controls_text_rect_height = len(controls_text) * 30
                controls_text_rect = pygame.Rect(20, HEIGHT - controls_text_rect_height - 20, 300, controls_text_rect_height)
                controls_text_surface = pygame.Surface((controls_text_rect.width, controls_text_rect.height), pygame.SRCALPHA)
                controls_text_surface.fill((64, 64, 64, 0))
                game_surface.blit(controls_text_surface, controls_text_rect)
                for i, line in enumerate(controls_text):
                    text_surface = font_hud.render(line, True, controls_text_color)
                    text_rect = text_surface.get_rect(topleft=(controls_text_rect.x + 10, controls_text_rect.y + i * 30))
                    game_surface.blit(text_surface, text_rect)
            game_surface.blit(mute_button['surface'], mute_button['rect'])
            game_surface.blit(mute_button['text'], mute_button['text_rect'])
            game_surface.blit(reset_button['text'], reset_button['text_rect'])
            apply_screen_shake(game_surface)
        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)
    pygame.quit()
asyncio.run(run_game())