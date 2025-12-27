import pygame
import sys
import random
import time
import math


pygame.init()
pygame.mixer.init()


TILE_SIZE = 30
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 182, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 182, 85)
DARK_BLUE = (0, 0, 139) # For scared ghosts

# Maps
LEVELS = [
    [
        "WWWWWWWWWWWWWWWWWWWW",
        "W..................W",
        "W.WW.WWW.WW.WWW.WW.W",
        "W.WW.WWW.WW.WWW.WW.W",
        "W.O................W",
        "W.WW.W.WWWWWW.W.WW.W",
        "W....W...WW...W....W",
        "WWWW.WWW.WW.WWW.WWWW",
        "   W.W...GG...W.W   ",
        "WWWW.W.WWWWWW.W.WWWW",
        "W..........P.......W",
        "W.WW.WWWWWWWWWW.WW.W",
        "W..W.....WW.....W..W",
        "WW.W.WWW.WW.WWW.W.WW",
        "W....W...O....W....W",
        "W.WWWW.WWWWWW.WWWW.W",
        "W..................W",
        "WWWWWWWWWWWWWWWWWWWW",
    ],
    [
        "WWWWWWWWWWWWWWWWWWWW",
        "W.O..W........W..O.W",
        "W.WW.W.WWWWWW.W.WW.W",
        "W..................W",
        "WW.W.WW.WWWW.WW.W.WW",
        "W..W....G..G....W..W",
        "W.WWWWWW.WW.WWWWWW.W",
        "W........WW........W",
        "WWWWWW.W.WW.W.WWWWWW",
        "W......W.GG.W......W",
        "W.WWWW.W.WW.W.WWWW.W",
        "W.O....W.P..W....O.W",
        "WWWWWW.WWWWWW.WWWWWW",
        "W..................W",
        "W.WW.WWWWWWWWWW.WW.W",
        "W..................W",
        "WWWWWWWWWWWWWWWWWWWW",
    ]
]

# Calculate screen dimensions based on the first map (assuming all are same size for now)
MAP_HEIGHT = len(LEVELS[0])
MAP_WIDTH = len(LEVELS[0][0])
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man 3002")
clock = pygame.time.Clock()

# Sound Manager
class SoundManager:
    def __init__(self):
        self.sounds = {}
        # Try to load sounds if they exist, otherwise silent
        sound_files = {
            'chomp': 'chomp.wav',
            'eat_ghost': 'eat_ghost.wav',
            'death': 'death.wav',
            'win': 'win.wav',
            'powerup': 'powerup.wav'
        }
        for name, file in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(file)
                self.sounds[name].set_volume(0.3)
            except:
                # print(f"Warning: Could not load sound {file}")
                self.sounds[name] = None

    def play(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()

sound_manager = SoundManager()

class Ghost:
    def __init__(self, x, y, color):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.normal_speed = 2
        self.scared_speed = 1
        self.speed = self.normal_speed
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.normal_color = color
        self.color = color
        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.change_direction()
        self.scared = False
        self.scared_timer = 0

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.rect.x = self.x * TILE_SIZE
        self.rect.y = self.y * TILE_SIZE
        self.scared = False
        self.color = self.normal_color
        self.speed = self.normal_speed
        self.change_direction()

    def change_direction(self):
        self.direction = random.choice(self.directions)

    def make_scared(self):
        self.scared = True
        self.scared_timer = pygame.time.get_ticks() + 5000 # 5 seconds
        self.color = DARK_BLUE
        self.speed = self.scared_speed

    def update(self, walls):
        # Handle scared timer
        if self.scared:
            if pygame.time.get_ticks() > self.scared_timer:
                self.scared = False
                self.color = self.normal_color
                self.speed = self.normal_speed

        # Move
        new_x = self.rect.x + self.direction[0] * self.speed
        new_y = self.rect.y + self.direction[1] * self.speed
        new_rect = pygame.Rect(new_x, new_y, TILE_SIZE, TILE_SIZE)

        # Check collision
        collision = False
        for wall in walls:
            if new_rect.colliderect(wall):
                collision = True
                break
        
        if not collision:
            self.rect = new_rect
        else:
            # Change direction on collision
            self.change_direction()

    def draw(self, surface):
        # Draw body (rounded top, rectangle bottom)
        x, y = self.rect.x, self.rect.y
        w, h = TILE_SIZE, TILE_SIZE
        
        # Head (semicircle)
        pygame.draw.circle(surface, self.color, (x + w//2, y + h//2), w//2)
        
        # Body (rectangle) - actually just fill the bottom half
        pygame.draw.rect(surface, self.color, (x, y + h//2, w, h//2))
        
        # Feet (3 small circles)
        foot_radius = w // 6
        for i in range(3):
            pygame.draw.circle(surface, self.color, (x + (2*i + 1) * foot_radius, y + h), foot_radius)
            
        # Eyes
        eye_radius = w // 5
        pupil_radius = eye_radius // 2
        eye_offset_x = w // 4
        eye_offset_y = h // 4
        
        # Eye positions
        left_eye_pos = (x + w//2 - eye_offset_x, y + eye_offset_y + h//4)
        right_eye_pos = (x + w//2 + eye_offset_x, y + eye_offset_y + h//4)
        
        # Draw Sclera (White part)
        pygame.draw.circle(surface, WHITE, left_eye_pos, eye_radius)
        pygame.draw.circle(surface, WHITE, right_eye_pos, eye_radius)
        
        # Draw Pupils (Blue part)
        # Offset pupils based on direction
        pupil_offset_x = self.direction[0] * 2
        pupil_offset_y = self.direction[1] * 2
        
        pupil_color = BLUE
        if self.scared:
            pupil_color = WHITE # Scared ghosts have different eyes usually, but let's keep it simple or maybe empty eyes
            # Actually scared ghosts are usually blue with white mouth/eyes. 
            # Current implementation sets color to DARK_BLUE when scared.
        
        pygame.draw.circle(surface, pupil_color, (left_eye_pos[0] + pupil_offset_x, left_eye_pos[1] + pupil_offset_y), pupil_radius)
        pygame.draw.circle(surface, pupil_color, (right_eye_pos[0] + pupil_offset_x, right_eye_pos[1] + pupil_offset_y), pupil_radius)

class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.score = 0
        self.speed = 5 
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.mouth_open_angle = 0
        self.mouth_speed = 5
        self.mouth_opening = True

    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y
        self.rect.x = self.x * TILE_SIZE
        self.rect.y = self.y * TILE_SIZE
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.mouth_open_angle = 0

    def update(self, walls):
        # Animation
        if self.direction != (0, 0):
            if self.mouth_opening:
                self.mouth_open_angle += self.mouth_speed
                if self.mouth_open_angle >= 45:
                    self.mouth_opening = False
            else:
                self.mouth_open_angle -= self.mouth_speed
                if self.mouth_open_angle <= 0:
                    self.mouth_opening = True
        else:
            self.mouth_open_angle = 0

        # Handle immediate reversal
        if self.next_direction != (0, 0):
            if (self.next_direction[0] == -self.direction[0] != 0) or \
               (self.next_direction[1] == -self.direction[1] != 0):
                self.direction = self.next_direction
                self.next_direction = (0, 0)

        # Try to change direction if aligned with grid
        if self.rect.x % TILE_SIZE == 0 and self.rect.y % TILE_SIZE == 0:
            if self.next_direction != (0, 0):
                next_x = self.rect.x + self.next_direction[0] * TILE_SIZE
                next_y = self.rect.y + self.next_direction[1] * TILE_SIZE
                next_rect = pygame.Rect(next_x, next_y, TILE_SIZE, TILE_SIZE)
                if not any(wall.colliderect(next_rect) for wall in walls):
                    self.direction = self.next_direction
                    self.next_direction = (0, 0)

        # Move in current direction
        if self.direction != (0, 0):
            new_x = self.rect.x + self.direction[0] * self.speed
            new_y = self.rect.y + self.direction[1] * self.speed
            new_rect = pygame.Rect(new_x, new_y, TILE_SIZE, TILE_SIZE)

            # Check collision with walls
            collision = False
            for wall in walls:
                if new_rect.colliderect(wall):
                    collision = True
                    break
            
            if not collision:
                self.rect = new_rect
            else:
                # Align to grid and stop
                self.rect.x = (round(self.rect.x / TILE_SIZE)) * TILE_SIZE
                self.rect.y = (round(self.rect.y / TILE_SIZE)) * TILE_SIZE
                self.direction = (0, 0)

    def draw(self, surface):
        center = (self.rect.centerx, self.rect.centery)
        radius = TILE_SIZE // 2 - 2
        
        if self.mouth_open_angle == 0:
             pygame.draw.circle(surface, YELLOW, center, radius)
        else:
            # Draw Pacman as a polygon (circle approximation) or circle with wedge removed
            # Easiest: Draw circle, then draw black triangle for mouth
            pygame.draw.circle(surface, YELLOW, center, radius)
            
            # Calculate mouth triangle points
            # Direction determines rotation
            angle_offset = 0
            if self.direction == (1, 0): # Right
                angle_offset = 0
            elif self.direction == (-1, 0): # Left
                angle_offset = 180
            elif self.direction == (0, -1): # Up
                angle_offset = 90
            elif self.direction == (0, 1): # Down
                angle_offset = 270
            
            # We need to draw a triangle that represents the mouth
            # Points: Center, and two points on the circumference
            
            p1 = center
            
            # Angle 1
            theta1 = math.radians(angle_offset - self.mouth_open_angle)
            x1 = center[0] + radius * math.cos(theta1)
            y1 = center[1] - radius * math.sin(theta1) # y is inverted in pygame
            
            # Angle 2
            theta2 = math.radians(angle_offset + self.mouth_open_angle)
            x2 = center[0] + radius * math.cos(theta2)
            y2 = center[1] - radius * math.sin(theta2)
            
            pygame.draw.polygon(surface, BLACK, [p1, (x1, y1), (x2, y2)])

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3

def draw_menu(screen, font, title_font):
    screen.fill(BLACK)
    title = title_font.render("PAC-MAN 3002", True, YELLOW)
    title_rect = title.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
    screen.blit(title, title_rect)
    
    start_text = font.render("Press SPACE to Start", True, WHITE)
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(start_text, start_rect)
    
    quit_text = font.render("Press Q to Quit", True, WHITE)
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
    screen.blit(quit_text, quit_rect)
    
    fullscreen_text = font.render("Press F11 to Toggle Fullscreen", True, WHITE)
    fullscreen_rect = fullscreen_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80))
    screen.blit(fullscreen_text, fullscreen_rect)

def main():
    global screen
    running = True
    game_state = MENU
    current_level_index = 0
    is_fullscreen = False
    
    # Game State Variables
    walls = []
    dots = []
    power_pellets = []
    ghosts = []
    player = None
    
    ghost_colors = [RED, PINK, CYAN, ORANGE]

    def load_level(level_index):
        nonlocal walls, dots, power_pellets, ghosts, player
        walls = []
        dots = []
        power_pellets = []
        ghosts = []
        player_pos = (1, 1)
        
        if level_index >= len(LEVELS):
            return False # No more levels

        level_map = LEVELS[level_index]
        ghost_color_index = 0

        for row_idx, row in enumerate(level_map):
            for col_idx, char in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                
                if char == 'W':
                    walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif char == '.':
                    dots.append(pygame.Rect(x + TILE_SIZE//2 - 2, y + TILE_SIZE//2 - 2, 4, 4))
                elif char == 'O':
                    power_pellets.append(pygame.Rect(x + TILE_SIZE//2 - 6, y + TILE_SIZE//2 - 6, 12, 12))
                elif char == 'P':
                    player_pos = (col_idx, row_idx)
                elif char == 'G':
                    ghosts.append(Ghost(col_idx, row_idx, ghost_colors[ghost_color_index % len(ghost_colors)]))
                    ghost_color_index += 1
        
        # Preserve score if player exists, else create new
        if player:
            score = player.score
            player = Player(player_pos[0], player_pos[1])
            player.score = score
        else:
            player = Player(player_pos[0], player_pos[1])
            
        return True

    # Load first level
    load_level(current_level_index)

    # Fonts
    font = pygame.font.SysFont('arial', 20)
    game_over_font = pygame.font.SysFont('arial', 48)
    title_font = pygame.font.SysFont('arial', 64, bold=True)
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

            if game_state == MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = PLAYING
                        current_level_index = 0
                        player = None
                        load_level(current_level_index)
                    elif event.key == pygame.K_q:
                        running = False
            
            elif game_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        player.next_direction = (1, 0)
                    elif event.key == pygame.K_UP:
                        player.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        player.next_direction = (0, 1)
            
            elif game_state == GAME_OVER or game_state == WIN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart from current level (preserve score)
                        load_level(current_level_index)
                        game_state = PLAYING
                    elif event.key == pygame.K_m:
                        game_state = MENU

        if game_state == PLAYING:
            # Update
            player.update(walls)
            
            for ghost in ghosts:
                ghost.update(walls)
                if player.rect.colliderect(ghost.rect):
                    if ghost.scared:
                        ghost.reset()
                        player.score += 200
                        sound_manager.play('eat_ghost')
                    else:
                        game_state = GAME_OVER
                        sound_manager.play('death')

            # Check dot collision
            for dot in dots[:]:
                if player.rect.colliderect(dot):
                    dots.remove(dot)
                    player.score += 10
                    # sound_manager.play('chomp') # Can be annoying if too frequent

            # Check power pellet collision
            for pellet in power_pellets[:]:
                if player.rect.colliderect(pellet):
                    power_pellets.remove(pellet)
                    player.score += 50
                    sound_manager.play('powerup')
                    for ghost in ghosts:
                        ghost.make_scared()
            
            # Check Level Complete
            if len(dots) == 0 and len(power_pellets) == 0:
                sound_manager.play('win')
                current_level_index += 1
                if not load_level(current_level_index):
                    game_state = WIN
                else:
                    # Small pause or transition could go here
                    pygame.time.delay(1000)
                    player.reset_position()

        # Drawing
        screen.fill(BLACK)
        
        if game_state == MENU:
            draw_menu(screen, font, title_font)
        
        elif game_state == PLAYING or game_state == GAME_OVER or game_state == WIN:
            # Draw walls
            for wall in walls:
                pygame.draw.rect(screen, BLUE, wall, border_radius=4)
                
            # Draw dots
            for dot in dots:
                pygame.draw.circle(screen, WHITE, dot.center, 2)

            # Draw power pellets
            for pellet in power_pellets:
                pygame.draw.circle(screen, WHITE, pellet.center, 6)
                
            # Draw player
            player.draw(screen)
            
            # Draw ghosts
            for ghost in ghosts:
                ghost.draw(screen)

            # Draw score and level
            score_text = font.render(f"Score: {player.score}  Level: {current_level_index + 1}", True, WHITE)
            screen.blit(score_text, (10, 10))

            if game_state == GAME_OVER:
                text = game_over_font.render("GAME OVER", True, RED)
                text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                screen.blit(text, text_rect)
                restart_text = font.render("Press R to Continue Level, M for Menu", True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
                screen.blit(restart_text, restart_rect)
                
            if game_state == WIN:
                text = game_over_font.render("YOU WIN!", True, GREEN)
                text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                screen.blit(text, text_rect)
                restart_text = font.render("Press R to Restart, M for Menu", True, WHITE)
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
                screen.blit(restart_text, restart_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
