import pygame
import sys
import os
import math

# Initialize pygame
pygame.init()

# Try to initialize mixer, but continue if it fails
try:
    pygame.mixer.init()
    audio_available = True
except:
    print("Warning: Audio initialization failed. Game will run without sound.")
    audio_available = False

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Get the current screen info to set proper fullscreen resolution
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Create the screen in fullscreen mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Combo Bros 2D - Character Select")

# Clock for controlling frame rate
clock = pygame.time.Clock()

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

# UI Colors
UI_PRIMARY = (45, 45, 55)
UI_SECONDARY = (65, 65, 75)
UI_ACCENT = (100, 149, 237)
UI_SUCCESS = (46, 204, 113)
UI_WARNING = (241, 196, 15)
UI_DANGER = (231, 76, 60)
UI_TEXT = (245, 245, 245)

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

# Character definitions
CHARACTERS = {
    'blaze': {
        'name': 'Blaze',
        'color': (255, 0, 0),  # Red
        'width': 50,
        'height': 80,
        'speed': 5,
        'jump_power': 15,
        'attack_power': 10,
        'special_power': 25,
        'description': 'Balanced fighter with fiery combat skills'
    },
    'verdant': {
        'name': 'Verdant',
        'color': (34, 139, 34),  # Green
        'width': 50,
        'height': 85,
        'speed': 4,
        'jump_power': 14,
        'attack_power': 12,
        'special_power': 30,
        'description': 'Nature warrior with powerful strikes but slower movement'
    },
    'nimbus': {
        'name': 'Nimbus',
        'color': (255, 192, 203),  # Pink
        'width': 45,
        'height': 45,
        'speed': 6,
        'jump_power': 18,
        'attack_power': 8,
        'special_power': 20,
        'description': 'Agile cloud spirit with high jumps and quick attacks'
    }
}

# Basic Button class
class Button:
    def __init__(self, x, y, width, height, text, color=UI_PRIMARY, hover_color=UI_ACCENT, text_color=UI_TEXT, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.font = font or font_medium
        self.clicked = False
        self.hover = False
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.hover else self.color
        return self.hover
    
    def is_clicked(self, pos, mouse_pressed):
        if self.rect.collidepoint(pos) and mouse_pressed and not self.clicked:
            self.clicked = True
            return True
        elif not mouse_pressed:
            self.clicked = False
        return False

# Character selection button
class CharacterButton:
    def __init__(self, x, y, character_key, character_data):
        self.rect = pygame.Rect(x, y, 200, 250)
        self.character_key = character_key
        self.character_data = character_data
        self.color = character_data['color']
        self.hover_color = tuple(min(255, c + 50) for c in character_data['color'])
        self.current_color = self.color
        self.selected = False
        self.hover = False
        self.clicked = False
        
        # Create character preview with pixelated human appearance
        self.preview = self._create_pixelated_human(character_data['width'], character_data['height'], character_data['color'])
        
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
        if color == RED:  # Blaze
            # Hat/flame-like hair
            for x in range(int(width * 0.2), int(width * 0.8), pixel_size):
                for y in range(0, int(head_height * 0.3), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        elif color == GREEN:  # Verdant
            # Leaf-like hair/hood
            for x in range(int(width * 0.15), int(width * 0.85), pixel_size):
                for y in range(0, int(head_height * 0.2), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            # Side foliage
            for x in range(int(width * 0.15), int(width * 0.25), pixel_size):
                for y in range(0, int(head_height * 0.6), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
            
            for x in range(int(width * 0.75), int(width * 0.85), pixel_size):
                for y in range(0, int(head_height * 0.6), pixel_size):
                    pygame.draw.rect(sprite, color, (x, y, pixel_size, pixel_size))
        
        elif color == PINK:  # Nimbus
            # Make more round and cloud-like
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
        
    def draw(self, surface):
        # Draw character card
        border_color = GOLD if self.selected else (WHITE if self.hover else GRAY)
        border_width = 4 if self.selected else 2
        
        # Card background with gradient
        for i in range(self.rect.height):
            ratio = i / self.rect.height
            color = tuple(max(0, min(255, c - int(50 * ratio))) for c in self.current_color)
            pygame.draw.line(surface, color, 
                           (self.rect.x, self.rect.y + i), 
                           (self.rect.x + self.rect.width, self.rect.y + i))
        
        # Card border
        pygame.draw.rect(surface, border_color, self.rect, border_width)
        
        # Character name
        name_text = font_medium.render(self.character_data['name'], True, WHITE)
        name_rect = name_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 10)
        surface.blit(name_text, name_rect)
        
        # Character preview
        preview_rect = self.preview.get_rect(center=(self.rect.centerx, self.rect.y + 100))
        surface.blit(self.preview, preview_rect)
        
        # Character stats
        stats_y = self.rect.y + 150
        stats = [
            f"Speed: {self.character_data['speed']}",
            f"Jump: {self.character_data['jump_power']}",
            f"Attack: {self.character_data['attack_power']}",
            f"Special: {self.character_data['special_power']}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = font_small.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(centerx=self.rect.centerx, y=stats_y + i * 25)
            surface.blit(stat_text, stat_rect)
        
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos)
        if self.hover != was_hover:
            self.current_color = self.hover_color if self.hover else self.color
        return self.hover
    
    def is_clicked(self, pos, mouse_pressed):
        if self.rect.collidepoint(pos) and mouse_pressed and not self.clicked:
            self.clicked = True
            return True
        elif not mouse_pressed:
            self.clicked = False
        return False

# Basic UI Panel class
class UIPanel:
    def __init__(self, x, y, width, height, title="", background_color=UI_PRIMARY):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.background_color = background_color
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.background_color, self.rect)
        pygame.draw.rect(surface, UI_ACCENT, self.rect, 2)
        
        if self.title:
            title_text = font_medium.render(self.title, True, WHITE)
            title_rect = title_text.get_rect(center=(self.rect.centerx, self.rect.y + 25))
            surface.blit(title_text, title_rect)

def show_character_select(vs_ai=False):
    """Character selection screen"""
    screen_center_x = SCREEN_WIDTH // 2
    screen_center_y = SCREEN_HEIGHT // 2
    
    selected_chars = {'player1': None, 'player2': None}
    current_player = 'player1'
    
    # Create character buttons
    char_buttons = []
    char_spacing = 250
    total_width = len(CHARACTERS) * char_spacing - 50
    start_x = screen_center_x - (total_width // 2)
    
    for i, (char_key, char_data) in enumerate(CHARACTERS.items()):
        x = start_x + i * char_spacing
        y = screen_center_y - 150
        button = CharacterButton(x, y, char_key, char_data)
        char_buttons.append(button)
    
    # Control buttons
    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 60, "Back", UI_DANGER, UI_DANGER)
    start_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60, "Start Game", UI_SUCCESS, UI_SUCCESS)
    
    # Player indicators
    player1_panel = UIPanel(50, 50, 300, 80, "Player 1: Select Character", RED)
    player2_panel = UIPanel(SCREEN_WIDTH - 350, 50, 300, 80, "Player 2: Select Character", BLUE)
    
    # Try to load sound effects
    try:
        select_sound = pygame.mixer.Sound("select.wav") if os.path.exists("select.wav") else None
        hover_sound = pygame.mixer.Sound("hover.wav") if os.path.exists("hover.wav") else None
    except:
        select_sound = hover_sound = None
    
    # Try to load music
    try:
        pygame.mixer.music.load("menu_music.mp3")
        pygame.mixer.music.play(-1)  # Loop indefinitely
        pygame.mixer.music.set_volume(0.5)
    except:
        pass
    
    # Animation variables
    animation_timer = 0
    
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
                if back_button.is_clicked(mouse_pos, True):
                    if select_sound:
                        select_sound.play()
                    return None, None
                    
                if start_button.is_clicked(mouse_pos, True):
                    if selected_chars['player1'] and (selected_chars['player2'] or vs_ai):
                        if vs_ai and not selected_chars['player2']:
                            # Auto-select AI character if not already selected
                            for char_key in CHARACTERS:
                                if char_key != selected_chars['player1']:
                                    selected_chars['player2'] = char_key
                                    break
                        if select_sound:
                            select_sound.play()
                        return selected_chars['player1'], selected_chars['player2']
                
                # Character selection
                for button in char_buttons:
                    if button.is_clicked(mouse_pos, True):
                        selected_chars[current_player] = button.character_key
                        button.selected = True
                        
                        if select_sound:
                            select_sound.play()
                        
                        # Switch to player 2 selection if not vs AI
                        if current_player == 'player1' and not vs_ai:
                            current_player = 'player2'
                        elif vs_ai:
                            # Auto-select AI character
                            for char_key in CHARACTERS:
                                if char_key != button.character_key:
                                    selected_chars['player2'] = char_key
                                    break
        
        # Update button hover states with sound
        for button in char_buttons:
            was_hover = button.hover
            button.check_hover(mouse_pos)
            if button.hover and not was_hover and hover_sound:
                hover_sound.play()
            
            # Update selected state
            button.selected = (button.character_key == selected_chars['player1'] or 
                             button.character_key == selected_chars['player2'])
        
        back_button.check_hover(mouse_pos)
        start_button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw animated background
        for y in range(0, SCREEN_HEIGHT, 10):
            color_value = 20 + int(10 * math.sin(animation_timer * 0.01 + y * 0.01))
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw title with animation
        title_y_offset = int(5 * math.sin(animation_timer * 0.05))
        title_text = font_title.render("Character Selection", True, WHITE)
        title_shadow = font_title.render("Character Selection", True, (50, 50, 50))
        
        title_rect = title_text.get_rect(center=(screen_center_x, 80 + title_y_offset))
        shadow_rect = title_shadow.get_rect(center=(screen_center_x + 3, 83 + title_y_offset))
        
        screen.blit(title_shadow, shadow_rect)
        screen.blit(title_text, title_rect)
        
        # Draw player indicators
        player1_panel.background_color = UI_ACCENT if current_player == 'player1' else UI_PRIMARY
        player2_panel.background_color = UI_ACCENT if current_player == 'player2' else UI_PRIMARY
        
        player1_panel.draw(screen)
        if not vs_ai:
            player2_panel.draw(screen)
        else:
            player2_panel.title = "Player 2: AI Opponent"
            player2_panel.draw(screen)
        
        # Draw character buttons with animations
        for button in char_buttons:
            # Add hover/selected animation
            original_y = button.rect.y
            if button.hover or button.selected:
                button.rect.y = original_y - int(3 * math.sin(animation_timer * 0.1))
            
            button.draw(screen)
            button.rect.y = original_y  # Reset position
        
        # Draw selected character info
        if selected_chars['player1']:
            char_data = CHARACTERS[selected_chars['player1']]
            p1_info = UIPanel(50, 150, 300, 100, f"Player 1: {char_data['name']}", char_data['color'])
            p1_info.draw(screen)
            
            desc_text = font_small.render(char_data['description'], True, WHITE)
            desc_rect = desc_text.get_rect(center=(p1_info.rect.centerx, p1_info.rect.y + 60))
            screen.blit(desc_text, desc_rect)
        
        if selected_chars['player2']:
            char_data = CHARACTERS[selected_chars['player2']]
            p2_info = UIPanel(SCREEN_WIDTH - 350, 150, 300, 100, 
                             f"{'AI' if vs_ai else 'Player 2'}: {char_data['name']}", 
                             char_data['color'])
            p2_info.draw(screen)
            
            desc_text = font_small.render(char_data['description'], True, WHITE)
            desc_rect = desc_text.get_rect(center=(p2_info.rect.centerx, p2_info.rect.y + 60))
            screen.blit(desc_text, desc_rect)
        
        # Draw control buttons
        back_button.draw(screen)
        start_button.draw(screen)
        
        # Draw instructions
        if not selected_chars['player1']:
            instruction = "Player 1: Choose your fighter!"
        elif not selected_chars['player2'] and not vs_ai:
            instruction = "Player 2: Choose your fighter!"
        else:
            instruction = "Ready to fight! Press Start Game!"
            
        instruction_bg = UIPanel(screen_center_x - 200, SCREEN_HEIGHT - 150, 400, 50)
        instruction_bg.draw(screen)
        
        instruction_text = font_medium.render(instruction, True, UI_TEXT)
        instruction_rect = instruction_text.get_rect(center=(screen_center_x, SCREEN_HEIGHT - 125))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    return None, None

if __name__ == "__main__":
    # Test the character selection screen
    player1_char, player2_char = show_character_select(vs_ai=False)
    print(f"Selected: Player 1 = {player1_char}, Player 2 = {player2_char}")
    pygame.quit()
