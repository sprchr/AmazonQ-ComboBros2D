import pygame
import sys
import os
import math
import random

# Initialize pygame
pygame.init()

# Try to initialize mixer, but continue if it fails
try:
    pygame.mixer.init()
    audio_available = True
except:
    print("Warning: Audio initialization failed. Game will run without sound.")
    audio_available = False

from character_select import (
    show_character_select, CHARACTERS, SCREEN_WIDTH, SCREEN_HEIGHT, 
    Button, UI_PRIMARY, UI_SECONDARY, UI_ACCENT, UI_SUCCESS, UI_DANGER, UI_WARNING, UI_TEXT
)
from difficulty_options import show_difficulty_options
from map_generator import generate_sky_map, create_platform_objects, get_map_name
from multiplayer import show_multiplayer_menu

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Create the screen in fullscreen mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Combo Bros 2D")

# Clock for controlling frame rate
clock = pygame.time.Clock()
MAX_FPS = 60  # Reduced from 240 to 60 for better game speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
PURPLE = (138, 43, 226)
ORANGE = (255, 140, 0)
CYAN = (0, 206, 209)
PINK = (255, 192, 203)
GRAY = (105, 105, 105)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (211, 211, 211)
GOLD = (255, 215, 0)

# Enhanced font system
try:
    font_title = pygame.font.Font(None, 72)
    font_large = pygame.font.Font(None, 56)
    font_medium = pygame.font.Font(None, 42)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 20)
except:
    font_title = pygame.font.SysFont('Arial', 72, bold=True)
    font_large = pygame.font.SysFont('Arial', 56, bold=True)
    font_medium = pygame.font.SysFont('Arial', 42)
    font_small = pygame.font.SysFont('Arial', 28)
    font_tiny = pygame.font.SysFont('Arial', 20)

# Game constants
GRAVITY = 0.8
FRICTION = 0.9
GROUND_Y = SCREEN_HEIGHT - 100
PLATFORM_HEIGHT = 20
MAX_HEALTH = 100
KNOCKBACK_FACTOR = 0.5

def draw_fps(surface, fps, font=None):
    """Draw the current FPS in the top left corner"""
    if font is None:
        font = pygame.font.SysFont('Arial', 20)
    
    # Determine color based on performance
    if fps >= 60:
        color = GREEN
    elif fps >= 30:
        color = YELLOW
    else:
        color = RED
    
    fps_text = font.render(f"FPS: {int(fps)}", True, color)
    surface.blit(fps_text, (10, 10))

# Player class
class Player:
    def __init__(self, character_key, player_num=1, is_ai=False):
        self.character_key = character_key
        self.character_data = CHARACTERS[character_key]
        self.player_num = player_num
        self.is_ai = is_ai
        
        # Position and movement
        self.x = SCREEN_WIDTH // 4 if player_num == 1 else 3 * SCREEN_WIDTH // 4
        self.y = GROUND_Y - self.character_data['height']
        self.width = self.character_data['width']
        self.height = self.character_data['height']
        self.vel_x = 0
        self.vel_y = 0
        self.speed = self.character_data['speed']
        self.jump_power = self.character_data['jump_power']
        self.facing_right = player_num == 1
        
        # Combat stats
        self.health = MAX_HEALTH
        self.attack_power = self.character_data['attack_power']
        self.special_power = self.character_data['special_power']
        self.damage_taken = 0
        self.knockback = 0
        
        # State tracking
        self.on_ground = True
        self.attacking = False
        self.special_attacking = False
        self.hit_cooldown = 0
        self.attack_cooldown = 0
        self.special_cooldown = 0
        self.stun_timer = 0
        self.jumps_left = 2  # Double jump
        
        # Animation variables - fixed to prevent duplication
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_state = "idle"
        self.animation_speed = 10  # Frames between animation updates
        
        # AI difficulty parameters
        self.ai_attack_chance = 0.1  # Default, will be overridden by difficulty
        self.ai_special_chance = 0.02
        self.ai_jump_chance = 0.02
        
        # Create character sprite - with pixelated human appearance
        self.sprite = self._create_pixelated_human(self.width, self.height, self.character_data['color'])
        
        # Hitbox for attacks
        self.attack_hitbox = pygame.Rect(0, 0, 0, 0)
        self.attack_active = False
        
        # Sound effects
        try:
            self.jump_sound = pygame.mixer.Sound("jump.wav") if os.path.exists("jump.wav") else None
            self.attack_sound = pygame.mixer.Sound("attack.wav") if os.path.exists("attack.wav") else None
            self.hit_sound = pygame.mixer.Sound("hit.wav") if os.path.exists("hit.wav") else None
            self.special_sound = pygame.mixer.Sound("special.wav") if os.path.exists("special.wav") else None
        except:
            self.jump_sound = self.attack_sound = self.hit_sound = self.special_sound = None
    
    def update(self, platforms, opponent=None, dt=1/60):
        # Apply gravity if not on ground
        if not self.on_ground:
            self.vel_y += GRAVITY * dt * 60  # Scale by dt and normalize to 60 FPS
        
        # Apply friction
        self.vel_x *= FRICTION
        
        # Update position with delta time
        self.x += self.vel_x * dt * 60  # Scale by dt and normalize to 60 FPS
        self.y += self.vel_y * dt * 60  # Scale by dt and normalize to 60 FPS
        
        # Check boundaries
        if self.x < 0:
            self.x = 0
            self.vel_x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.vel_x = 0
        
        # Check if on ground or platform
        self.on_ground = False
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True
            self.jumps_left = 2
        
        # Check platform collisions
        for platform in platforms:
            if (self.vel_y > 0 and  # Moving downward
                self.y + self.height >= platform.y and
                self.y + self.height <= platform.y + PLATFORM_HEIGHT and
                self.x + self.width > platform.x and
                self.x < platform.x + platform.width):
                self.y = platform.y - self.height
                self.vel_y = 0
                self.on_ground = True
                self.jumps_left = 2
        
        # Update cooldowns - scale by delta time
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt * 60  # Scale by dt and normalize to 60 FPS
            if self.hit_cooldown < 0:
                self.hit_cooldown = 0
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt * 60  # Scale by dt and normalize to 60 FPS
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 0
                self.attacking = False
                self.attack_active = False
        
        if self.special_cooldown > 0:
            self.special_cooldown -= dt * 60  # Scale by dt and normalize to 60 FPS
            if self.special_cooldown <= 0:
                self.special_cooldown = 0
                self.special_attacking = False
        
        if self.stun_timer > 0:
            self.stun_timer -= dt * 60  # Scale by dt and normalize to 60 FPS
            if self.stun_timer < 0:
                self.stun_timer = 0
        
        # Update attack hitbox if attacking or special attacking
        if (self.attacking or self.special_attacking) and self.attack_active:
            if self.attacking:
                # Regular attack hitbox
                hitbox_width = self.width * 1.5
                hitbox_height = self.height * 0.6
                
                if self.facing_right:
                    self.attack_hitbox = pygame.Rect(
                        self.x + self.width * 0.8,
                        self.y + self.height * 0.2,
                        hitbox_width,
                        hitbox_height
                    )
                else:
                    self.attack_hitbox = pygame.Rect(
                        self.x - hitbox_width * 0.8,
                        self.y + self.height * 0.2,
                        hitbox_width,
                        hitbox_height
                    )
            
            # Special attacks hitboxes are created in their respective methods
            
            # Check if hit opponent
            if opponent and self.attack_hitbox.colliderect(pygame.Rect(opponent.x, opponent.y, opponent.width, opponent.height)):
                if opponent.hit_cooldown == 0:
                    # Calculate damage based on attack type
                    if self.attacking:
                        damage = self.attack_power * (1 + self.damage_taken / 100)
                        knockback_x = 10 + self.damage_taken * 0.2
                        knockback_y = -8 - self.damage_taken * 0.1
                    else:  # special attack
                        damage = self.special_power * (1 + self.damage_taken / 100)
                        
                        # Character-specific knockback for special attacks
                        if self.character_key == 'blaze':
                            # Fire Nova - explosive knockback
                            dx = opponent.x - self.x
                            dy = opponent.y - self.y
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist > 0:
                                knockback_x = dx/dist * 15
                                knockback_y = dy/dist * 15 - 5  # Upward component
                            else:
                                knockback_x = 15 if self.facing_right else -15
                                knockback_y = -15
                                
                        elif self.character_key == 'verdant':
                            # Vine Whip - strong horizontal knockback
                            knockback_x = 20 if self.facing_right else -20
                            knockback_y = -5
                            
                        elif self.character_key == 'nimbus':
                            # Cloud Dash - upward knockback
                            knockback_x = 8 if self.facing_right else -8
                            knockback_y = -18
                        else:
                            # Default knockback
                            knockback_x = 15 if self.facing_right else -15
                            knockback_y = -10
                    
                    if not self.facing_right:
                        knockback_x *= -1
                    
                    opponent.take_hit(damage, knockback_x, knockback_y)
                    self.attack_active = False  # Prevent multiple hits
        
        # Update animation timer (controlled by animation_speed)
        self.animation_timer += dt * 60  # Scale by dt and normalize to 60 FPS
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
        # AI logic if this is an AI player
        if self.is_ai and opponent and self.stun_timer == 0:
            self.update_ai(opponent, dt)
    
    def update_ai(self, opponent, dt=1/60):
        # Simple AI: move toward opponent and attack when close
        distance_x = opponent.x - self.x
        distance_y = opponent.y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)
        
        # Update facing direction
        self.facing_right = distance_x > 0
        
        # Move toward opponent
        if abs(distance_x) > 100:
            if distance_x > 0:
                self.move_right(dt)
            else:
                self.move_left(dt)
        
        # Jump if opponent is above or if on same level and random chance
        if (distance_y < -50 or (abs(distance_x) < 200 and random.random() < self.ai_jump_chance * dt * 60)) and self.jumps_left > 0:
            self.jump()
        
        # Attack if close enough
        if abs(distance_x) < 120 and abs(distance_y) < 80:
            if random.random() < self.ai_attack_chance * dt * 60:
                self.attack()
            elif random.random() < self.ai_special_chance * dt * 60:
                self.special_attack()
    
    def move_left(self, dt=1/60):
        if self.stun_timer == 0:
            self.vel_x = -self.speed * dt * 60  # Scale by dt and normalize to 60 FPS
            self.facing_right = False
            self.animation_state = "run"
    
    def move_right(self, dt=1/60):
        if self.stun_timer == 0:
            self.vel_x = self.speed * dt * 60  # Scale by dt and normalize to 60 FPS
            self.facing_right = True
            self.animation_state = "run"
    
    def jump(self):
        if self.stun_timer == 0 and self.jumps_left > 0:
            self.vel_y = -self.jump_power
            self.jumps_left -= 1
            self.on_ground = False
            self.animation_state = "jump"
            
            if self.jump_sound:
                self.jump_sound.play()
    
    def attack(self):
        if self.stun_timer == 0 and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_active = True
            self.attack_cooldown = 20
            self.animation_state = "attack"
            
            if self.attack_sound:
                self.attack_sound.play()
    
    def special_attack(self):
        if self.stun_timer == 0 and self.special_cooldown == 0:
            self.special_attacking = True
            self.special_cooldown = 60
            self.animation_state = "special"
            
            # Character-specific special attacks
            if self.character_key == 'blaze':
                # Blaze: Fire Nova - damages opponents in a larger radius
                self.perform_blaze_special()
            elif self.character_key == 'verdant':
                # Verdant: Vine Whip - longer range attack with knockback
                self.perform_verdant_special()
            elif self.character_key == 'nimbus':
                # Nimbus: Cloud Dash - quick movement with invulnerability
                self.perform_nimbus_special()
            
            if self.special_sound:
                self.special_sound.play()
    
    def perform_blaze_special(self):
        # Fire Nova - creates a damaging area around Blaze
        self.attack_hitbox = pygame.Rect(
            self.x - self.width,
            self.y - self.height,
            self.width * 3,
            self.height * 3
        )
        self.attack_active = True
        # Special effect will be handled in the draw method
    
    def perform_verdant_special(self):
        # Vine Whip - extended range attack in facing direction
        hitbox_width = self.width * 3
        hitbox_height = self.height * 0.8
        
        if self.facing_right:
            self.attack_hitbox = pygame.Rect(
                self.x + self.width * 0.5,
                self.y + self.height * 0.1,
                hitbox_width,
                hitbox_height
            )
        else:
            self.attack_hitbox = pygame.Rect(
                self.x - hitbox_width * 0.9,
                self.y + self.height * 0.1,
                hitbox_width,
                hitbox_height
            )
        self.attack_active = True
    
    def perform_nimbus_special(self):
        # Cloud Dash - quick movement with temporary invulnerability
        dash_power = 15
        if self.facing_right:
            self.vel_x = dash_power
        else:
            self.vel_x = -dash_power
        
        self.vel_y = -5  # Small upward boost
        self.hit_cooldown = 30  # Temporary invulnerability
    
    def _create_pixelated_human(self, width, height, color):
        """Create a pixelated human-like sprite"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Define pixel size for the pixelated look
        pixel_size = max(2, min(width, height) // 10)
        
        # Calculate body proportions
        head_height = height * 0.25
        body_height = height * 0.4
        legs_height = height * 0.35
        
        # Head (slightly smaller than body width)
        head_width = width * 0.7
        head_x = (width - head_width) / 2
        
        # Draw head (pixelated circle)
        head_radius = head_width / 2
        head_center_x = width / 2
        head_center_y = head_height / 2
        
        # Draw pixelated head
        for x in range(0, width, pixel_size):
            for y in range(0, int(head_height), pixel_size):
                # Calculate distance from center of head
                dx = x + pixel_size/2 - head_center_x
                dy = y + pixel_size/2 - head_center_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance <= head_radius:
                    # Slightly lighter color for head
                    head_color = tuple(min(255, c + 30) for c in color)
                    pygame.draw.rect(sprite, head_color, (x, y, pixel_size, pixel_size))
        
        # Draw body (pixelated rectangle)
        body_y = head_height
        for x in range(int(width * 0.2), int(width * 0.8), pixel_size):
            for y in range(int(body_y), int(body_y + body_height), pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Draw arms (pixelated rectangles)
        arm_width = width * 0.15
        # Left arm
        for x in range(0, int(width * 0.2), pixel_size):
            for y in range(int(body_y + body_height * 0.1), int(body_y + body_height * 0.6), pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Right arm
        for x in range(int(width * 0.8), width, pixel_size):
            for y in range(int(body_y + body_height * 0.1), int(body_y + body_height * 0.6), pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Draw legs (pixelated rectangles)
        legs_y = head_height + body_height
        leg_width = width * 0.25
        
        # Left leg
        for x in range(int(width * 0.25), int(width * 0.45), pixel_size):
            for y in range(int(legs_y), height, pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Right leg
        for x in range(int(width * 0.55), int(width * 0.75), pixel_size):
            for y in range(int(legs_y), height, pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Add face details (simple eyes and mouth)
        eye_size = max(1, pixel_size // 2)
        eye_y = head_height * 0.4
        
        # Left eye
        pygame.draw.rect(sprite, (0, 0, 0), 
                       (int(width * 0.35), int(eye_y), eye_size, eye_size))
        
        # Right eye
        pygame.draw.rect(sprite, (0, 0, 0), 
                       (int(width * 0.65), int(eye_y), eye_size, eye_size))
        
        # Mouth
        mouth_width = width * 0.3
        pygame.draw.rect(sprite, (0, 0, 0), 
                       (int(width/2 - mouth_width/2), int(head_height * 0.6), 
                        int(mouth_width), eye_size))
        
        # Add character-specific details based on color
        # For example, different hairstyles or accessories
        if color == RED:  # Mario-like
            # Hat
            for x in range(int(width * 0.2), int(width * 0.8), pixel_size):
                for y in range(0, int(head_height * 0.3), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        elif color == GREEN:  # Link-like
            # Hat/hair
            for x in range(int(width * 0.15), int(width * 0.85), pixel_size):
                for y in range(0, int(head_height * 0.2), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            # Hair on sides
            for x in range(int(width * 0.15), int(width * 0.25), pixel_size):
                for y in range(0, int(head_height * 0.6), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            for x in range(int(width * 0.75), int(width * 0.85), pixel_size):
                for y in range(0, int(head_height * 0.6), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        elif color == PINK:  # Kirby-like
            # Make more round
            sprite.fill((0, 0, 0, 0))  # Clear sprite
            
            # Draw a more circular character
            for x in range(0, width, pixel_size):
                for y in range(0, height, pixel_size):
                    # Calculate distance from center
                    dx = x + pixel_size/2 - width/2
                    dy = y + pixel_size/2 - height/2
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance <= width/2:
                        pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            # Add eyes
            pygame.draw.rect(sprite, (0, 0, 0), 
                           (int(width * 0.3), int(height * 0.3), eye_size*2, eye_size*2))
            pygame.draw.rect(sprite, (0, 0, 0), 
                           (int(width * 0.7), int(height * 0.3), eye_size*2, eye_size*2))
            
            # Add mouth
            mouth_width = width * 0.4
            pygame.draw.rect(sprite, (0, 0, 0), 
                           (int(width/2 - mouth_width/2), int(height * 0.5), 
                            int(mouth_width), eye_size*2))
        
        return sprite
    
    def _create_pixelated_human(self, width, height, color):
        """Create a pixelated human-like sprite"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Define pixel size for the pixelated look
        pixel_size = max(2, min(width, height) // 10)
        
        # Calculate body proportions
        head_height = height * 0.25
        body_height = height * 0.4
        legs_height = height * 0.35
        
        # Head (slightly smaller than body width)
        head_width = width * 0.7
        head_x = (width - head_width) / 2
        
        # Draw head (pixelated circle)
        head_radius = head_width / 2
        head_center_x = width / 2
        head_center_y = head_height / 2
        
        # Draw pixelated head
        for x in range(0, width, pixel_size):
            for y in range(0, int(head_height), pixel_size):
                # Calculate distance from center of head
                dx = x + pixel_size/2 - head_center_x
                dy = y + pixel_size/2 - head_center_y
                distance = (dx**2 + dy**2)**0.5
                
                if distance <= head_radius:
                    # Slightly lighter color for head
                    head_color = tuple(min(255, c + 30) for c in color)
                    pygame.draw.rect(sprite, head_color, (x, y, pixel_size, pixel_size))
        
        # Draw body (pixelated rectangle)
        body_y = head_height
        for x in range(int(width * 0.2), int(width * 0.8), pixel_size):
            for y in range(int(body_y), int(body_y + body_height), pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Draw arms (pixelated rectangles)
        arm_width = width * 0.15
        # Left arm
        for x in range(0, int(width * 0.2), pixel_size):
            for y in range(int(body_y + body_height * 0.1), int(body_y + body_height * 0.6), pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Right arm
        for x in range(int(width * 0.8), width, pixel_size):
            for y in range(int(body_y + body_height * 0.1), int(body_y + body_height * 0.6), pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Draw legs (pixelated rectangles)
        legs_y = head_height + body_height
        leg_width = width * 0.25
        
        # Left leg
        for x in range(int(width * 0.25), int(width * 0.45), pixel_size):
            for y in range(int(legs_y), height, pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Right leg
        for x in range(int(width * 0.55), int(width * 0.75), pixel_size):
            for y in range(int(legs_y), height, pixel_size):
                pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        # Add face details (simple eyes and mouth)
        eye_size = max(1, pixel_size // 2)
        eye_y = head_height * 0.4
        
        # Left eye
        pygame.draw.rect(sprite, (0, 0, 0), 
                       (int(width * 0.35), int(eye_y), eye_size, eye_size))
        
        # Right eye
        pygame.draw.rect(sprite, (0, 0, 0), 
                       (int(width * 0.65), int(eye_y), eye_size, eye_size))
        
        # Mouth
        mouth_width = width * 0.3
        pygame.draw.rect(sprite, (0, 0, 0), 
                       (int(width/2 - mouth_width/2), int(head_height * 0.6), 
                        int(mouth_width), eye_size))
        
        # Add character-specific details based on color
        # For example, different hairstyles or accessories
        if color == RED:  # Mario-like
            # Hat
            for x in range(int(width * 0.2), int(width * 0.8), pixel_size):
                for y in range(0, int(head_height * 0.3), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        elif color == GREEN:  # Link-like
            # Hat/hair
            for x in range(int(width * 0.15), int(width * 0.85), pixel_size):
                for y in range(0, int(head_height * 0.2), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            # Hair on sides
            for x in range(int(width * 0.15), int(width * 0.25), pixel_size):
                for y in range(0, int(head_height * 0.6), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            for x in range(int(width * 0.75), int(width * 0.85), pixel_size):
                for y in range(0, int(head_height * 0.6), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        elif color == PINK:  # Kirby-like
            # Make more round
            sprite.fill((0, 0, 0, 0))  # Clear sprite
            
            # Draw a more circular character
            for x in range(0, width, pixel_size):
                for y in range(0, height, pixel_size):
                    # Calculate distance from center
                    dx = x + pixel_size/2 - width/2
                    dy = y + pixel_size/2 - height/2
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance <= width/2:
                        pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            # Add eyes
            pygame.draw.rect(sprite, (0, 0, 0), 
                           (int(width * 0.3), int(height * 0.3), eye_size*2, eye_size*2))
            pygame.draw.rect(sprite, (0, 0, 0), 
                           (int(width * 0.7), int(height * 0.3), eye_size*2, eye_size*2))
            
            # Add mouth
            mouth_width = width * 0.4
            pygame.draw.rect(sprite, (0, 0, 0), 
                           (int(width/2 - mouth_width/2), int(height * 0.5), 
                            int(mouth_width), eye_size*2))
        
        return sprite
    
    def take_hit(self, damage, knockback_x, knockback_y):
        self.damage_taken += damage
        self.health = max(0, MAX_HEALTH - self.damage_taken)  # Fix: properly calculate health based on damage
        
        # Apply knockback based on damage taken
        knockback_multiplier = 1 + (self.damage_taken / 50)
        self.vel_x = knockback_x * knockback_multiplier
        self.vel_y = knockback_y * knockback_multiplier
        
        self.stun_timer = int(damage * 2)
        self.hit_cooldown = 30
        self.animation_state = "hit"
        
        if self.hit_sound:
            self.hit_sound.play()
    
    def draw(self, surface):
        # Draw character with animation effects
        sprite_copy = self.sprite.copy()
        
        # Flash when hit
        if self.hit_cooldown > 0 and self.hit_cooldown % 4 < 2:
            sprite_copy.fill(WHITE)
        
        # Draw character sprite (only once)
        surface.blit(sprite_copy, (self.x, self.y))
        
        # Draw attack effect (only when attacking)
        if self.attacking:
            attack_effect = pygame.Surface((self.width * 1.5, self.height * 0.6), pygame.SRCALPHA)
            attack_effect.fill((255, 255, 255, 128))
            
            if self.facing_right:
                surface.blit(attack_effect, (self.x + self.width * 0.8, self.y + self.height * 0.2))
            else:
                surface.blit(attack_effect, (self.x - self.width * 1.2, self.y + self.height * 0.2))
        
        # Draw special attack effect (only when special attacking)
        if self.special_attacking:
            # Character-specific special attack visuals
            if self.character_key == 'blaze':
                # Fire Nova effect - expanding circle
                radius = 50 + 20 * math.sin(self.animation_timer * 0.2)
                for i in range(8):
                    angle = i * (2 * math.pi / 8) + self.animation_timer * 0.1
                    effect_x = self.x + self.width/2 + radius * math.cos(angle)
                    effect_y = self.y + self.height/2 + radius * math.sin(angle)
                    
                    effect_size = 25 + 10 * math.sin(self.animation_timer * 0.3 + i)
                    effect = pygame.Surface((effect_size, effect_size), pygame.SRCALPHA)
                    
                    # Fire colors
                    fire_color = (255, 100 + int(155 * math.sin(self.animation_timer * 0.2)), 0, 180)
                    pygame.draw.circle(effect, fire_color, (effect_size//2, effect_size//2), effect_size//2)
                    
                    surface.blit(effect, (effect_x - effect_size/2, effect_y - effect_size/2))
                
                # Center fire effect
                center_effect = pygame.Surface((self.width * 2, self.height * 2), pygame.SRCALPHA)
                pygame.draw.circle(center_effect, (255, 200, 50, 100), 
                                 (self.width, self.height), self.width * 0.8)
                surface.blit(center_effect, (self.x - self.width/2, self.y - self.height/2))
                
            elif self.character_key == 'verdant':
                # Vine Whip effect - extending green tendrils
                whip_length = self.width * 3
                whip_width = 15
                start_x = self.x + self.width/2
                start_y = self.y + self.height/2
                
                # Direction based on facing
                direction = 1 if self.facing_right else -1
                
                # Draw multiple vine segments with wave pattern
                segments = 8
                for i in range(segments):
                    segment_length = whip_length / segments
                    segment_x = start_x + direction * i * segment_length
                    
                    # Wave pattern
                    wave_offset = math.sin(self.animation_timer * 0.2 + i) * 20
                    segment_y = start_y + wave_offset
                    
                    # Next point
                    next_x = start_x + direction * (i + 1) * segment_length
                    next_y = start_y + math.sin(self.animation_timer * 0.2 + i + 1) * 20
                    
                    # Gradient color from dark to light green
                    green_val = 100 + int(155 * (i / segments))
                    vine_color = (30, green_val, 30, 200)
                    
                    # Draw vine segment
                    pygame.draw.line(surface, vine_color, 
                                   (segment_x, segment_y), 
                                   (next_x, next_y), 
                                   whip_width - i)
                    
                    # Draw leaf at the end
                    if i == segments - 1:
                        leaf_size = 25
                        leaf = pygame.Surface((leaf_size, leaf_size), pygame.SRCALPHA)
                        pygame.draw.ellipse(leaf, (50, 220, 50, 200), 
                                         (0, 0, leaf_size, leaf_size))
                        surface.blit(leaf, (next_x - leaf_size/2, next_y - leaf_size/2))
                
            elif self.character_key == 'nimbus':
                # Cloud Dash effect - trail of clouds and speed lines
                
                # Speed lines
                for i in range(10):
                    line_length = 30 + i * 5
                    line_x = self.x + self.width/2
                    line_y = self.y + self.height/2
                    
                    # Direction based on facing
                    direction = 1 if self.facing_right else -1
                    end_x = line_x - direction * line_length
                    
                    # Randomize position slightly
                    offset_y = random.randint(-20, 20)
                    
                    # Fade based on animation timer
                    alpha = 200 - (self.animation_timer % 10) * 20
                    line_color = (200, 200, 255, max(0, alpha))
                    
                    # Draw speed line
                    pygame.draw.line(surface, line_color, 
                                   (line_x, line_y + offset_y), 
                                   (end_x, line_y + offset_y), 
                                   2)
                
                # Cloud trail
                for i in range(3):
                    # Position based on facing direction
                    direction = 1 if self.facing_right else -1
                    cloud_x = self.x + self.width/2 - direction * (i * 20 + 30)
                    cloud_y = self.y + self.height/2
                    
                    # Cloud size and opacity based on distance
                    cloud_size = 30 - i * 5
                    opacity = 150 - i * 40
                    
                    # Draw cloud puffs
                    cloud = pygame.Surface((cloud_size * 2, cloud_size), pygame.SRCALPHA)
                    for j in range(3):
                        puff_x = j * cloud_size/2
                        puff_color = (255, 255, 255, opacity)
                        pygame.draw.circle(cloud, puff_color, 
                                         (puff_x, cloud_size/2), 
                                         cloud_size/2)
                    
                    surface.blit(cloud, (cloud_x - cloud_size, cloud_y - cloud_size/2))
        
        # Draw player number indicator
        indicator_color = RED if self.player_num == 1 else BLUE
        pygame.draw.circle(surface, indicator_color, (int(self.x + self.width/2), int(self.y - 15)), 10)
        
        # Draw health bar
        health_width = 80
        health_height = 10
        health_x = self.x + self.width/2 - health_width/2
        health_y = self.y - 30
        
        # Health bar background
        pygame.draw.rect(surface, GRAY, (health_x, health_y, health_width, health_height))
        
        # Health bar fill
        health_fill_width = int(health_width * (self.health / MAX_HEALTH))
        health_color = GREEN
        if self.health < MAX_HEALTH * 0.6:
            health_color = YELLOW
        if self.health < MAX_HEALTH * 0.3:
            health_color = RED
            
        pygame.draw.rect(surface, health_color, (health_x, health_y, health_fill_width, health_height))
        
        # Draw damage percentage
        damage_text = font_small.render(f"{int(self.damage_taken)}%", True, WHITE)
        surface.blit(damage_text, (self.x + self.width/2 - damage_text.get_width()/2, self.y - 50))


# Platform class
class Platform:
    def __init__(self, x, y, width, height=PLATFORM_HEIGHT, color=GRAY):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y, self.width, self.height), 2)


# Particle effect class
class Particle:
    def __init__(self, x, y, color, size=5, velocity_x=0, velocity_y=0, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.age = 0
    
    def update(self, dt=1/60):
        self.x += self.velocity_x * dt * 60  # Scale by dt and normalize to 60 FPS
        self.y += self.velocity_y * dt * 60  # Scale by dt and normalize to 60 FPS
        self.velocity_y += 0.1 * dt * 60  # Gravity, scaled by dt
        self.age += dt * 60  # Scale by dt and normalize to 60 FPS
        return self.age < self.lifetime
    
    def draw(self, surface):
        alpha = 255 * (1 - self.age / self.lifetime)
        color_with_alpha = (*self.color, alpha)
        
        # Draw with transparency
        particle_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (self.size//2, self.size//2), self.size//2)
        surface.blit(particle_surface, (int(self.x), int(self.y)))


def draw_text_in_box(surface, text, font, color, rect, align="center"):
    """Draw text that fits within a rectangle, with proper alignment
    
    Args:
        surface: Surface to draw on
        text: Text to draw
        font: Font to use
        color: Text color
        rect: Rectangle to contain the text (pygame.Rect)
        align: Text alignment ("left", "center", or "right")
    """
    # Check if text fits in the box
    text_surface = font.render(text, True, color)
    
    if text_surface.get_width() > rect.width:
        # Text is too wide, need to truncate or scale
        # Try smaller font first
        try:
            smaller_font = pygame.font.Font(font.get_filename(), int(font.get_height() * 0.8))
            return draw_text_in_box(surface, text, smaller_font, color, rect, align)
        except:
            # If can't get smaller font, truncate with ellipsis
            chars_that_fit = 0
            while chars_that_fit < len(text):
                test_text = text[:chars_that_fit] + "..."
                test_surface = font.render(test_text, True, color)
                if test_surface.get_width() <= rect.width:
                    text = test_text
                    text_surface = test_surface
                    break
                chars_that_fit += 1
    
    # Position text based on alignment
    if align == "left":
        text_rect = text_surface.get_rect(midleft=(rect.left, rect.centery))
    elif align == "right":
        text_rect = text_surface.get_rect(midright=(rect.right, rect.centery))
    else:  # center
        text_rect = text_surface.get_rect(center=rect.center)
    
    surface.blit(text_surface, text_rect)

# Game state functions
def create_stage(difficulty="Normal"):
    """Create platforms for the stage"""
    # Generate random sky map
    platform_data, map_type = generate_sky_map(
        SCREEN_WIDTH, 
        SCREEN_HEIGHT, 
        PLATFORM_HEIGHT, 
        GROUND_Y,
        difficulty
    )
    
    # Convert platform data to Platform objects
    platforms = create_platform_objects(platform_data, Platform)
    
    # Get map name
    map_name = get_map_name(map_type)
    
    return platforms, map_name


def show_countdown(map_name="Sky Battle"):
    """Show countdown before match starts"""
    # Show map name first
    screen.fill(BLACK)
    
    # Draw map name
    map_title = font_large.render(f"Map: {map_name}", True, GOLD)
    map_rect = map_title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(map_title, map_rect)
    
    # Draw "GET READY" text
    ready_text = font_medium.render("Get ready for battle!", True, WHITE)
    ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(ready_text, ready_rect)
    
    pygame.display.flip()
    pygame.time.delay(1500)
    
    # Countdown
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        
        # Draw countdown number
        count_text = font_title.render(str(i), True, WHITE)
        count_rect = count_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(count_text, count_rect)
        
        # Draw "GET READY" text
        ready_text = font_large.render("GET READY!", True, GOLD)
        ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(ready_text, ready_rect)
        
        pygame.display.flip()
        pygame.time.delay(1000)
    
    # Show "FIGHT!"
    screen.fill(BLACK)
    fight_text = font_title.render("FIGHT!", True, RED)
    fight_rect = fight_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(fight_text, fight_rect)
    pygame.display.flip()
    pygame.time.delay(1000)


def show_winner(winner):
    """Show the winner screen"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Draw winner text
    winner_text = font_title.render(f"{winner.character_data['name']} WINS!", True, GOLD)
    winner_rect = winner_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(winner_text, winner_rect)
    
    # Draw winner character
    winner_sprite = pygame.transform.scale(winner.sprite, (winner.width * 2, winner.height * 2))
    sprite_rect = winner_sprite.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
    screen.blit(winner_sprite, sprite_rect)
    
    # Draw continue text
    continue_text = font_medium.render("Press ENTER to continue", True, WHITE)
    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
    screen.blit(continue_text, continue_rect)
    
    pygame.display.flip()
    
    # Clear all pending events to prevent button state issues
    pygame.event.clear()
    
    # Wait for a short delay to prevent accidental key presses
    pygame.time.delay(500)
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    waiting = False
        clock.tick(MAX_FPS)
    
    # Clear all events again before returning to menu
    pygame.event.clear()


def draw_background(timer, map_name="Sky Battle"):
    """Draw animated background"""
    # Sky gradient background
    for y in range(0, SCREEN_HEIGHT, 2):
        # Create a blue gradient for sky
        ratio = y / SCREEN_HEIGHT
        blue = 180 - int(100 * ratio)
        green = 200 - int(150 * ratio)
        red = 100 - int(50 * ratio)
        
        # Add some variation based on timer
        blue_var = int(10 * math.sin(timer * 0.01 + y * 0.01))
        
        color = (red, green, min(255, blue + blue_var))
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
    
    # Draw clouds
    for i in range(20):
        x = (timer * (i % 5 + 1) * 0.2 + i * 100) % (SCREEN_WIDTH + 200) - 100
        y = (i * 40 + math.sin(timer * 0.01 + i) * 20) % (GROUND_Y - 100)
        size = 30 + math.sin(timer * 0.05 + i) * 10
        
        # Draw a fluffy cloud (multiple circles)
        cloud_color = (255, 255, 255, 150)  # White with transparency
        cloud_surface = pygame.Surface((size * 3, size * 2), pygame.SRCALPHA)
        
        pygame.draw.circle(cloud_surface, cloud_color, (size, size), size)
        pygame.draw.circle(cloud_surface, cloud_color, (size * 1.5, size * 0.7), size * 0.8)
        pygame.draw.circle(cloud_surface, cloud_color, (size * 0.5, size * 0.7), size * 0.7)
        pygame.draw.circle(cloud_surface, cloud_color, (size * 2, size), size * 0.9)
        
        screen.blit(cloud_surface, (int(x), int(y)))
    
    # Draw stars in the background
    for i in range(50):
        x = (i * 50 + math.sin(timer * 0.01 + i) * 10) % SCREEN_WIDTH
        y = (i * 20 + math.cos(timer * 0.01 + i) * 10) % (GROUND_Y - 200)
        size = 1 + math.sin(timer * 0.05 + i) * 1
        
        # Make stars twinkle
        brightness = 150 + int(100 * math.sin(timer * 0.1 + i * 0.3))
        star_color = (brightness, brightness, brightness)
        
        pygame.draw.circle(screen, star_color, (int(x), int(y)), int(size))
    
    # Draw map name in a box to prevent overflow
    name_rect = pygame.Rect(SCREEN_WIDTH - 300, 40, 280, 40)
    draw_text_in_box(screen, map_name, font_medium, WHITE, name_rect, "right")


def run_game(player1_char, player2_char, vs_ai=False, difficulty="Normal"):
    """Main game function"""
    # Create players
    player1 = Player(player1_char, player_num=1)
    player2 = Player(player2_char, player_num=2, is_ai=vs_ai)
    
    # Apply difficulty settings to AI
    if vs_ai:
        if difficulty == "Easy":
            player2.speed *= 0.7
            player2.attack_power *= 0.8
            player2.special_power *= 0.8
            ai_attack_chance = 0.05
            ai_special_chance = 0.01
            ai_jump_chance = 0.01
        elif difficulty == "Normal":
            # Default settings
            ai_attack_chance = 0.1
            ai_special_chance = 0.02
            ai_jump_chance = 0.02
        elif difficulty == "Hard":
            player2.speed *= 1.2
            player2.attack_power *= 1.2
            player2.special_power *= 1.2
            ai_attack_chance = 0.15
            ai_special_chance = 0.03
            ai_jump_chance = 0.03
        elif difficulty == "Insane":
            player2.speed *= 1.5
            player2.attack_power *= 1.5
            player2.special_power *= 1.5
            player2.jump_power *= 1.2
            ai_attack_chance = 0.2
            ai_special_chance = 0.05
            ai_jump_chance = 0.05
    
    # Create stage
    platforms, map_name = create_stage(difficulty)
    
    # Create particle effects list
    particles = []
    
    # Animation timer
    animation_timer = 0
    
    # Time tracking for frame-independent movement
    last_time = pygame.time.get_ticks()
    
    # Show countdown
    show_countdown(map_name)
    
    # Try to load music
    try:
        pygame.mixer.music.load("battle_music.mp3")
        pygame.mixer.music.play(-1)  # Loop indefinitely
        pygame.mixer.music.set_volume(0.7)
    except:
        pass
    
    # Main game loop
    running = True
    game_over = False
    winner = None
    
    # FPS tracking variables
    fps_update_timer = 0
    current_fps = 0
    
    while running:
        # Calculate delta time (time since last frame in seconds)
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0  # Convert to seconds
        last_time = current_time
        
        # Cap delta time to prevent large jumps
        if dt > 0.1:
            dt = 0.1
        
        animation_timer += 1
        fps_update_timer += 1
        
        # Update FPS display every 10 frames
        if fps_update_timer >= 10:
            current_fps = clock.get_fps()
            fps_update_timer = 0
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Player 1 controls
                if not game_over and player1.stun_timer == 0:
                    if event.key == pygame.K_w:
                        player1.jump()
                    if event.key == pygame.K_a:
                        player1.move_left()
                    if event.key == pygame.K_d:
                        player1.move_right()
                    if event.key == pygame.K_f or event.key == pygame.K_n:
                        player1.attack()
                    if event.key == pygame.K_g or event.key == pygame.K_m:
                        player1.special_attack()
                
                # Player 2 controls (if not AI)
                if not vs_ai and not game_over and player2.stun_timer == 0:
                    if event.key == pygame.K_UP:
                        player2.jump()
                    if event.key == pygame.K_LEFT:
                        player2.move_left()
                    if event.key == pygame.K_RIGHT:
                        player2.move_right()
                    if event.key == pygame.K_COMMA or event.key == pygame.K_n:
                        player2.attack()
                    if event.key == pygame.K_PERIOD or event.key == pygame.K_m:
                        player2.special_attack()
        
        # Continuous key press handling
        if not game_over:
            keys = pygame.key.get_pressed()
            
            # Player 1 movement
            if keys[pygame.K_a]:
                player1.move_left(dt)
            if keys[pygame.K_d]:
                player1.move_right(dt)
            
            # Player 2 movement (if not AI)
            if not vs_ai:
                if keys[pygame.K_LEFT]:
                    player2.move_left(dt)
                if keys[pygame.K_RIGHT]:
                    player2.move_right(dt)
        
        # Update players
        if not game_over:
            # Update AI behavior based on difficulty
            if vs_ai:
                # Override AI behavior in Player.update_ai
                player2.ai_attack_chance = ai_attack_chance
                player2.ai_special_chance = ai_special_chance
                player2.ai_jump_chance = ai_jump_chance
            
            player1.update(platforms, player2, dt)
            player2.update(platforms, player1, dt)
            
            # Check for game over
            if player1.health <= 0:
                game_over = True
                winner = player2
            elif player2.health <= 0:
                game_over = True
                winner = player1
        
        # Update particles
        particles = [p for p in particles if p.update(dt)]
        
        # Add particles for special effects
        if player1.special_attacking and animation_timer % 3 == 0:
            # Character-specific particles
            if player1.character_key == 'blaze':
                # Fire particles
                for _ in range(8):
                    particles.append(Particle(
                        player1.x + player1.width/2,
                        player1.y + player1.height/2,
                        (255, random.randint(100, 200), 0),  # Orange-red
                        size=random.randint(5, 12),
                        velocity_x=random.uniform(-5, 5),
                        velocity_y=random.uniform(-5, 5),
                        lifetime=random.randint(20, 40)
                    ))
            elif player1.character_key == 'verdant':
                # Leaf particles
                for _ in range(5):
                    particles.append(Particle(
                        player1.x + player1.width/2 + (player1.width if player1.facing_right else -player1.width),
                        player1.y + player1.height/2,
                        (random.randint(30, 100), random.randint(150, 255), random.randint(30, 100)),  # Green shades
                        size=random.randint(4, 8),
                        velocity_x=random.uniform(-3, 3) + (5 if player1.facing_right else -5),
                        velocity_y=random.uniform(-2, 2),
                        lifetime=random.randint(30, 50)
                    ))
            elif player1.character_key == 'nimbus':
                # Cloud particles
                for _ in range(6):
                    particles.append(Particle(
                        player1.x + player1.width/2 - (player1.width if player1.facing_right else -player1.width),
                        player1.y + player1.height/2,
                        (255, 255, 255),  # White
                        size=random.randint(8, 15),
                        velocity_x=random.uniform(-2, 2) - (3 if player1.facing_right else -3),
                        velocity_y=random.uniform(-1, 1),
                        lifetime=random.randint(15, 30)
                    ))
        
        if player2.special_attacking and animation_timer % 3 == 0:
            # Character-specific particles
            if player2.character_key == 'blaze':
                # Fire particles
                for _ in range(8):
                    particles.append(Particle(
                        player2.x + player2.width/2,
                        player2.y + player2.height/2,
                        (255, random.randint(100, 200), 0),  # Orange-red
                        size=random.randint(5, 12),
                        velocity_x=random.uniform(-5, 5),
                        velocity_y=random.uniform(-5, 5),
                        lifetime=random.randint(20, 40)
                    ))
            elif player2.character_key == 'verdant':
                # Leaf particles
                for _ in range(5):
                    particles.append(Particle(
                        player2.x + player2.width/2 + (player2.width if player2.facing_right else -player2.width),
                        player2.y + player2.height/2,
                        (random.randint(30, 100), random.randint(150, 255), random.randint(30, 100)),  # Green shades
                        size=random.randint(4, 8),
                        velocity_x=random.uniform(-3, 3) + (5 if player2.facing_right else -5),
                        velocity_y=random.uniform(-2, 2),
                        lifetime=random.randint(30, 50)
                    ))
            elif player2.character_key == 'nimbus':
                # Cloud particles
                for _ in range(6):
                    particles.append(Particle(
                        player2.x + player2.width/2 - (player2.width if player2.facing_right else -player2.width),
                        player2.y + player2.height/2,
                        (255, 255, 255),  # White
                        size=random.randint(8, 15),
                        velocity_x=random.uniform(-2, 2) - (3 if player2.facing_right else -3),
                        velocity_y=random.uniform(-1, 1),
                        lifetime=random.randint(15, 30)
                    ))
        
        # Draw everything
        screen.fill(BLACK)  # Clear the screen completely before drawing
        draw_background(animation_timer, map_name)
        
        # Draw platforms
        for platform in platforms:
            platform.draw(screen)
        
        # Draw players
        player1.draw(screen)
        player2.draw(screen)
        
        # Draw particles
        for particle in particles:
            particle.draw(screen)
        
        # Draw UI
        # Timer
        timer_text = font_medium.render(f"Time: {animation_timer // 60}", True, WHITE)
        screen.blit(timer_text, (SCREEN_WIDTH//2 - timer_text.get_width()//2, 20))
        
        # Player names
        p1_name = font_small.render(f"P1: {player1.character_data['name']}", True, RED)
        screen.blit(p1_name, (20, 50))
        
        p2_name = font_small.render(f"P2: {player2.character_data['name']}", True, BLUE)
        screen.blit(p2_name, (SCREEN_WIDTH - p2_name.get_width() - 20, 20))
        
        # Draw FPS counter in top left
        draw_fps(screen, current_fps, font_tiny)
        
        # Draw difficulty if vs AI
        if vs_ai:
            diff_text = font_small.render(f"Difficulty: {difficulty}", True, GOLD)
            screen.blit(diff_text, (SCREEN_WIDTH//2 - diff_text.get_width()//2, 60))
        
        # Show winner
        if game_over and winner:
            show_winner(winner)
            running = False
        
        pygame.display.flip()
        clock.tick(MAX_FPS)
    
    return


def main_menu():
    """Main menu function"""
    animation_timer = 0
    
    # Try to load music
    try:
        pygame.mixer.music.load("menu_music.mp3")
        pygame.mixer.music.play(-1)  # Loop indefinitely
        pygame.mixer.music.set_volume(0.5)
    except:
        pass
    
    # Clear all events before starting menu
    pygame.event.clear()
    
    # Create buttons
    button_width = 300
    button_height = 80
    button_x = SCREEN_WIDTH//2 - button_width//2
    
    vs_player_button = Button(button_x, 200, button_width, button_height, "VS Player", UI_PRIMARY, UI_ACCENT)
    vs_ai_button = Button(button_x, 300, button_width, button_height, "VS Computer", UI_PRIMARY, UI_ACCENT)
    multiplayer_button = Button(button_x, 400, button_width, button_height, "Online Multiplayer", UI_PRIMARY, UI_ACCENT)
    options_button = Button(button_x, 500, button_width, button_height, "Difficulty Options", UI_PRIMARY, UI_ACCENT)
    quit_button = Button(button_x, 600, button_width, button_height, "Quit Game", UI_DANGER, UI_DANGER)
    
    # Default difficulty
    difficulty = "Normal"
    
    # Online player count (fixed to show accurate number)
    online_players = 0  # Default to 0 players when no one is online
    
    running = True
    while running:
        animation_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Reset button clicked states each frame
        vs_player_button.clicked = False
        vs_ai_button.clicked = False
        multiplayer_button.clicked = False
        options_button.clicked = False
        quit_button.clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                mouse_pos = event.pos  # Get position from event for accuracy
                
                if vs_player_button.rect.collidepoint(mouse_pos):
                    # Clear events before character selection
                    pygame.event.clear()
                    player1_char, player2_char = show_character_select(vs_ai=False)
                    if player1_char and player2_char:
                        run_game(player1_char, player2_char, vs_ai=False, difficulty=difficulty)
                
                elif vs_ai_button.rect.collidepoint(mouse_pos):
                    # Clear events before character selection
                    pygame.event.clear()
                    player1_char, player2_char = show_character_select(vs_ai=True)
                    if player1_char and player2_char:
                        run_game(player1_char, player2_char, vs_ai=True, difficulty=difficulty)
                
                elif multiplayer_button.rect.collidepoint(mouse_pos):
                    # Clear events before multiplayer menu
                    pygame.event.clear()
                    show_multiplayer_menu(screen, clock)
                
                elif options_button.rect.collidepoint(mouse_pos):
                    # Clear events before options screen
                    pygame.event.clear()
                    difficulty = show_difficulty_options(
                        screen, font_title, font_medium, font_small, font_tiny,
                        BLACK, WHITE, GOLD, GRAY, LIGHT_GRAY,
                        UI_PRIMARY, UI_SECONDARY, UI_ACCENT, UI_SUCCESS, UI_WARNING, UI_DANGER,
                        SCREEN_WIDTH, SCREEN_HEIGHT, Button, clock, difficulty
                    )
                
                elif quit_button.rect.collidepoint(mouse_pos):
                    running = False
        
        # Update button hover states
        vs_player_button.check_hover(mouse_pos)
        vs_ai_button.check_hover(mouse_pos)
        multiplayer_button.check_hover(mouse_pos)
        options_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        # Keep online player count stable
        # No need to change the count randomly
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw animated background
        for y in range(0, SCREEN_HEIGHT, 5):
            color_value = 20 + int(10 * math.sin(animation_timer * 0.01 + y * 0.01))
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw title with animation
        title_y_offset = int(5 * math.sin(animation_timer * 0.05))
        title_text = font_title.render("Combo Bros 2D", True, WHITE)
        title_shadow = font_title.render("Combo Bros 2D", True, (50, 50, 50))
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100 + title_y_offset))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 3, 103 + title_y_offset))
        
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = font_medium.render("Choose Your Game Mode", True, GOLD)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw current difficulty
        diff_text = font_small.render(f"Current Difficulty: {difficulty}", True, GOLD)
        diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH//2, 220))
        screen.blit(diff_text, diff_rect)
        
        # Draw buttons
        vs_player_button.draw(screen)
        vs_ai_button.draw(screen)
        multiplayer_button.draw(screen)
        options_button.draw(screen)
        quit_button.draw(screen)
        
        # Draw online player count in top right
        player_count_bg = pygame.Rect(SCREEN_WIDTH - 180, 20, 160, 40)
        pygame.draw.rect(screen, UI_ACCENT, player_count_bg, border_radius=10)
        pygame.draw.rect(screen, WHITE, player_count_bg, 2, border_radius=10)
        
        # Draw player icon
        pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH - 150, 40), 10)
        pygame.draw.circle(screen, UI_ACCENT, (SCREEN_WIDTH - 150, 35), 3)  # Head
        pygame.draw.rect(screen, UI_ACCENT, (SCREEN_WIDTH - 155, 40, 10, 10))  # Body
        
        # Draw count with appropriate text
        count_text = font_small.render(f"Online: {online_players}" if online_players > 0 else "No players online", True, WHITE)
        count_rect = count_text.get_rect(midleft=(SCREEN_WIDTH - 130, 40))
        screen.blit(count_text, count_rect)
        
        # Draw footer
        footer_text = font_small.render("© 2025 Combo Bros 2D", True, GRAY)
        footer_rect = footer_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
        screen.blit(footer_text, footer_rect)
        
        pygame.display.flip()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    main_menu()
    pygame.quit()
    sys.exit()
def show_difficulty_options(current_difficulty):
    """Show difficulty options screen"""
    animation_timer = 0
    
    # Create difficulty buttons
    button_width = 300
    button_height = 80
    button_x = SCREEN_WIDTH//2 - button_width//2
    
    easy_button = Button(button_x, 250, button_width, button_height, "Easy", UI_PRIMARY, UI_SUCCESS)
    normal_button = Button(button_x, 350, button_width, button_height, "Normal", UI_PRIMARY, UI_ACCENT)
    hard_button = Button(button_x, 450, button_width, button_height, "Hard", UI_PRIMARY, UI_WARNING)
    insane_button = Button(button_x, 550, button_width, button_height, "Insane", UI_PRIMARY, UI_DANGER)
    back_button = Button(50, SCREEN_HEIGHT - 100, 150, 60, "Back", UI_SECONDARY, UI_ACCENT)
    
    # Highlight current difficulty
    if current_difficulty == "Easy":
        easy_button.current_color = UI_SUCCESS
    elif current_difficulty == "Normal":
        normal_button.current_color = UI_ACCENT
    elif current_difficulty == "Hard":
        hard_button.current_color = UI_WARNING
    elif current_difficulty == "Insane":
        insane_button.current_color = UI_DANGER
    
    running = True
    while running:
        animation_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.is_clicked(mouse_pos, True):
                    current_difficulty = "Easy"
                    easy_button.current_color = UI_SUCCESS
                    normal_button.current_color = UI_PRIMARY
                    hard_button.current_color = UI_PRIMARY
                    insane_button.current_color = UI_PRIMARY
                
                if normal_button.is_clicked(mouse_pos, True):
                    current_difficulty = "Normal"
                    easy_button.current_color = UI_PRIMARY
                    normal_button.current_color = UI_ACCENT
                    hard_button.current_color = UI_PRIMARY
                    insane_button.current_color = UI_PRIMARY
                
                if hard_button.is_clicked(mouse_pos, True):
                    current_difficulty = "Hard"
                    easy_button.current_color = UI_PRIMARY
                    normal_button.current_color = UI_PRIMARY
                    hard_button.current_color = UI_WARNING
                    insane_button.current_color = UI_PRIMARY
                
                if insane_button.is_clicked(mouse_pos, True):
                    current_difficulty = "Insane"
                    easy_button.current_color = UI_PRIMARY
                    normal_button.current_color = UI_PRIMARY
                    hard_button.current_color = UI_PRIMARY
                    insane_button.current_color = UI_DANGER
                
                if back_button.is_clicked(mouse_pos, True):
                    return current_difficulty
        
        # Update button hover states
        easy_button.check_hover(mouse_pos)
        normal_button.check_hover(mouse_pos)
        hard_button.check_hover(mouse_pos)
        insane_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw animated background
        for y in range(0, SCREEN_HEIGHT, 5):
            color_value = 20 + int(10 * math.sin(animation_timer * 0.01 + y * 0.01))
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw title with animation
        title_y_offset = int(5 * math.sin(animation_timer * 0.05))
        title_text = font_title.render("Difficulty Options", True, WHITE)
        title_shadow = font_title.render("Difficulty Options", True, (50, 50, 50))
        
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100 + title_y_offset))
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH//2 + 3, 103 + title_y_offset))
        
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_text = font_medium.render("Select Game Difficulty", True, GOLD)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Draw buttons
        easy_button.draw(screen)
        normal_button.draw(screen)
        hard_button.draw(screen)
        insane_button.draw(screen)
        back_button.draw(screen)
        
        # Draw difficulty descriptions
        desc_x = SCREEN_WIDTH - 400
        desc_y = 250
        desc_height = 80
        
        descriptions = {
            "Easy": "AI moves slower and attacks less frequently",
            "Normal": "Balanced AI difficulty for casual play",
            "Hard": "AI is more aggressive and reacts faster",
            "Insane": "AI has enhanced abilities and perfect timing"
        }
        
        # Highlight current description
        current_desc_y = desc_y
        if current_difficulty == "Easy":
            current_desc_y = desc_y
        elif current_difficulty == "Normal":
            current_desc_y = desc_y + desc_height
        elif current_difficulty == "Hard":
            current_desc_y = desc_y + desc_height * 2
        elif current_difficulty == "Insane":
            current_desc_y = desc_y + desc_height * 3
        
        # Draw highlight box for current description
        pygame.draw.rect(screen, UI_ACCENT, (desc_x - 10, current_desc_y - 10, 380, desc_height), 2)
        
        # Draw all descriptions
        for i, (diff, desc) in enumerate(descriptions.items()):
            diff_color = WHITE
            if diff == current_difficulty:
                diff_color = GOLD
            
            diff_text = font_small.render(diff + ":", True, diff_color)
            desc_text = font_tiny.render(desc, True, LIGHT_GRAY)
            
            screen.blit(diff_text, (desc_x, desc_y + i * desc_height))
            screen.blit(desc_text, (desc_x, desc_y + i * desc_height + 30))
        
        pygame.display.flip()
        clock.tick(MAX_FPS)
    
    return current_difficulty
def draw_text_in_box(surface, text, font, color, rect, align="center"):
    """Draw text that fits within a rectangle, with proper alignment
    
    Args:
        surface: Surface to draw on
        text: Text to draw
        font: Font to use
        color: Text color
        rect: Rectangle to contain the text (pygame.Rect)
        align: Text alignment ("left", "center", or "right")
    """
    # Check if text fits in the box
    text_surface = font.render(text, True, color)
    
    if text_surface.get_width() > rect.width:
        # Text is too wide, need to truncate or scale
        # Try smaller font first
        try:
            smaller_font = pygame.font.Font(font.get_filename(), int(font.get_height() * 0.8))
            return draw_text_in_box(surface, text, smaller_font, color, rect, align)
        except:
            # If can't get smaller font, truncate with ellipsis
            chars_that_fit = 0
            while chars_that_fit < len(text):
                test_text = text[:chars_that_fit] + "..."
                test_surface = font.render(test_text, True, color)
                if test_surface.get_width() <= rect.width:
                    text = test_text
                    text_surface = test_surface
                    break
                chars_that_fit += 1
    
    # Position text based on alignment
    if align == "left":
        text_rect = text_surface.get_rect(midleft=(rect.left, rect.centery))
    elif align == "right":
        text_rect = text_surface.get_rect(midright=(rect.right, rect.centery))
    else:  # center
        text_rect = text_surface.get_rect(center=rect.center)
    
    surface.blit(text_surface, text_rect)
def draw_text_in_box(surface, text, font, color, rect, align="center"):
    """Draw text that fits within a rectangle, with proper alignment
    
    Args:
        surface: Surface to draw on
        text: Text to draw
        font: Font to use
        color: Text color
        rect: Rectangle to contain the text (pygame.Rect)
        align: Text alignment ("left", "center", or "right")
    """
    # Check if text fits in the box
    text_surface = font.render(text, True, color)
    
    if text_surface.get_width() > rect.width:
        # Text is too wide, need to truncate or scale
        # Try smaller font first
        try:
            smaller_font = pygame.font.Font(font.get_filename(), int(font.get_height() * 0.8))
            return draw_text_in_box(surface, text, smaller_font, color, rect, align)
        except:
            # If can't get smaller font, truncate with ellipsis
            chars_that_fit = 0
            while chars_that_fit < len(text):
                test_text = text[:chars_that_fit] + "..."
                test_surface = font.render(test_text, True, color)
                if test_surface.get_width() <= rect.width:
                    text = test_text
                    text_surface = test_surface
                    break
                chars_that_fit += 1
    
    # Position text based on alignment
    if align == "left":
        text_rect = text_surface.get_rect(midleft=(rect.left, rect.centery))
    elif align == "right":
        text_rect = text_surface.get_rect(midright=(rect.right, rect.centery))
    else:  # center
        text_rect = text_surface.get_rect(center=rect.center)
    
    surface.blit(text_surface, text_rect)
