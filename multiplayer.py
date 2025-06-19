import pygame
import sys
import math
import random

# Import constants from main game
from character_select import SCREEN_WIDTH, SCREEN_HEIGHT, UI_PRIMARY, UI_SECONDARY, UI_ACCENT, UI_SUCCESS, UI_DANGER, UI_WARNING

# Define fonts
font_title = pygame.font.Font(None, 72)
font_large = pygame.font.Font(None, 56)
font_medium = pygame.font.Font(None, 42)
font_small = pygame.font.Font(None, 28)
font_tiny = pygame.font.Font(None, 20)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GREEN = (34, 139, 34)
YELLOW = (255, 215, 0)
GOLD = (255, 215, 0)
LIGHT_GRAY = (211, 211, 211)

# Network constants
DEFAULT_PORT = 5555

# Global variables to track hosted rooms and active clients
HOSTED_ROOMS = []
ACTIVE_CLIENTS = {}  # Dictionary to store active client instances by username
CURRENT_USERNAME = ""  # Track the current username for the session
CURRENT_HOSTED_ROOM = None  # Track the currently hosted room

# Flag to prevent rooms from being marked as inactive
KEEP_ROOMS_ACTIVE = True

# Dummy classes for testing without network
class GameClient:
    def __init__(self):
        self.connected = False
        self.callbacks = {}
        self.username = ""
        self.current_room = None
        self.is_host = False
    
    def connect(self, host, port, username):
        self.connected = True
        self.username = username
        
        # Store this client in the active clients dictionary
        ACTIVE_CLIENTS[username] = self
        
        if "on_connect" in self.callbacks:
            self.callbacks["on_connect"]({"username": username})
        return True
    
    def disconnect(self):
        # Save the current room info before disconnecting
        was_host = self.is_host
        current_room = self.current_room
        
        # Only remove from active clients if we're actually disconnecting
        # from the server, not just closing a menu
        if self.username in ACTIVE_CLIENTS:
            del ACTIVE_CLIENTS[self.username]
        
        # If we were hosting a room, make sure it stays active
        if was_host and current_room and KEEP_ROOMS_ACTIVE:
            for room in HOSTED_ROOMS:
                if room["room_id"] == current_room:
                    room["active"] = True
                    break
            
        self.connected = False
        if "on_disconnect" in self.callbacks:
            self.callbacks["on_disconnect"]()
    
    def join_room(self, room_id):
        global CURRENT_HOSTED_ROOM
        self.current_room = room_id
        
        # Check if this is a new room (hosting)
        is_new_room = True
        for room in HOSTED_ROOMS:
            if room["room_id"] == room_id:
                is_new_room = False
                break
        
        # If it's a new room, add it to the hosted rooms list
        if is_new_room:
            new_room = {
                "room_id": room_id,
                "host": self.username,
                "map": "Random Map",
                "players": 1,
                "max_players": 6,
                "active": True
            }
            HOSTED_ROOMS.append(new_room)
            self.is_host = True
            
            # Track the currently hosted room
            CURRENT_HOSTED_ROOM = room_id
            
            # Trigger room created callback
            if "on_room_created" in self.callbacks:
                self.callbacks["on_room_created"](room_id)
        else:
            # We're joining an existing room
            self.is_host = False
            
            # Update player count in the room
            for room in HOSTED_ROOMS:
                if room["room_id"] == room_id:
                    room["players"] += 1
                    break
        
        # Trigger room joined callback
        if "on_room_joined" in self.callbacks:
            players = ["Host"]
            for client_name, client in ACTIVE_CLIENTS.items():
                if client.current_room == room_id and client_name != self.username:
                    players.append(client_name)
            
            self.callbacks["on_room_joined"](room_id, players, "Random Map", "Joined successfully")
    
    def leave_room(self):
        if self.current_room:
            room_id = self.current_room
            self.current_room = None
            
            # If we're the host, DON'T mark the room as inactive if KEEP_ROOMS_ACTIVE is True
            if self.is_host:
                for room in HOSTED_ROOMS:
                    if room["room_id"] == room_id:
                        if KEEP_ROOMS_ACTIVE:
                            # Keep the room active
                            room["active"] = True
                        else:
                            room["active"] = False
                        break
            else:
                # Otherwise just decrease the player count
                for room in HOSTED_ROOMS:
                    if room["room_id"] == room_id:
                        room["players"] = max(1, room["players"] - 1)
                        break
    
    def get_available_rooms(self):
        if "on_room_list" in self.callbacks:
            # Start with actual hosted rooms
            rooms = []
            
            # Add active hosted rooms first (these are the real rooms)
            for room in HOSTED_ROOMS:
                if room.get("active", True):  # Only include active rooms
                    rooms.append(room)
            
            # Only add dummy rooms if no real rooms exist (for testing purposes)
            if not rooms:
                rooms = [
                    {"room_id": "room1", "host": "Player1", "map": "Sky Battle", "players": 1, "max_players": 6},
                    {"room_id": "room2", "host": "Player2", "map": "Forest Arena", "players": 2, "max_players": 4}
                ]
            
            self.callbacks["on_room_list"](rooms)
    
    def send_chat(self, message, room_id=None):
        if "on_chat" in self.callbacks:
            self.callbacks["on_chat"]("You", message, room_id)
            
            # Broadcast to other clients in the same room
            for client_name, client in ACTIVE_CLIENTS.items():
                if client_name != self.username and client.current_room == room_id:
                    if "on_chat" in client.callbacks:
                        client.callbacks["on_chat"](self.username, message, room_id)
    
    def set_callback(self, event, callback):
        self.callbacks[event] = callback

class TextInput:
    def __init__(self, x, y, width, height, placeholder, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.font = font
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < 20:  # Limit text length
                if event.unicode.isprintable():
                    self.text += event.unicode
    
    def draw(self, surface):
        # Draw background
        bg_color = UI_SECONDARY if self.active else UI_PRIMARY
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        # Draw text or placeholder
        if self.text:
            text_surface = self.font.render(self.text, True, WHITE)
        else:
            text_surface = self.font.render(self.placeholder, True, LIGHT_GRAY)
        
        # Center text vertically and align left with padding
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)
        
        # Draw cursor if active
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer // 30 % 2 == 0:  # Blink every 30 frames
                if self.text:
                    cursor_x = text_rect.right + 2
                else:
                    cursor_x = self.rect.x + 10
                
                pygame.draw.line(surface, WHITE, 
                               (cursor_x, self.rect.y + 10), 
                               (cursor_x, self.rect.y + self.rect.height - 10), 2)

class ChatBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.messages = []
        self.scroll_offset = 0
        self.max_messages = 100
        self.visible_messages = height // 30  # Approx. lines that fit
    
    def add_message(self, sender, text):
        self.messages.append({"sender": sender, "text": text, "time": pygame.time.get_ticks()})
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # Auto-scroll to bottom
        self.scroll_offset = max(0, len(self.messages) - self.visible_messages)
    
    def scroll_up(self):
        self.scroll_offset = max(0, self.scroll_offset - 1)
    
    def scroll_down(self):
        self.scroll_offset = min(max(0, len(self.messages) - self.visible_messages), self.scroll_offset + 1)
    
    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, UI_PRIMARY, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        # Draw messages
        visible_messages = self.messages[self.scroll_offset:self.scroll_offset + self.visible_messages]
        
        for i, msg in enumerate(visible_messages):
            # Determine sender color
            if msg["sender"] == "System":
                sender_color = YELLOW
            elif msg["sender"] == "Error":
                sender_color = RED
            elif msg["sender"] == "You":
                sender_color = GREEN
            else:
                sender_color = BLUE
            
            # Format message
            sender_text = font_small.render(f"{msg['sender']}: ", True, sender_color)
            message_text = font_small.render(msg["text"], True, WHITE)
            
            # Draw message
            surface.blit(sender_text, (self.rect.x + 10, self.rect.y + 10 + i * 30))
            surface.blit(message_text, (self.rect.x + 10 + sender_text.get_width(), self.rect.y + 10 + i * 30))
        
        # Draw scroll indicators if needed
        if self.scroll_offset > 0:
            pygame.draw.polygon(surface, WHITE, [
                (self.rect.right - 20, self.rect.y + 15),
                (self.rect.right - 10, self.rect.y + 5),
                (self.rect.right - 30, self.rect.y + 5)
            ])
        
        if self.scroll_offset + self.visible_messages < len(self.messages):
            pygame.draw.polygon(surface, WHITE, [
                (self.rect.right - 20, self.rect.bottom - 15),
                (self.rect.right - 10, self.rect.bottom - 5),
                (self.rect.right - 30, self.rect.bottom - 5)
            ])

class PlayerCountDisplay:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.count = 0
        self.max_count = 0
        self.animation_timer = 0
    
    def update(self, count, max_count=4):
        self.count = count
        self.max_count = max_count
    
    def draw(self, surface):
        self.animation_timer += 1
        
        # Draw background
        bg_rect = pygame.Rect(self.x - 50, self.y - 25, 100, 50)
        pygame.draw.rect(surface, UI_PRIMARY, bg_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, bg_rect, 2, border_radius=10)
        
        # Draw player icons
        for i in range(self.max_count):
            icon_x = self.x - 35 + i * 25
            icon_y = self.y
            
            if i < self.count:
                # Active player
                pygame.draw.circle(surface, GREEN, (icon_x, icon_y), 10)
                pygame.draw.circle(surface, WHITE, (icon_x, icon_y), 10, 1)
            else:
                # Empty slot
                pygame.draw.circle(surface, UI_SECONDARY, (icon_x, icon_y), 8)
                pygame.draw.circle(surface, LIGHT_GRAY, (icon_x, icon_y), 8, 1)

class Button:
    def __init__(self, x, y, width, height, text, color=UI_PRIMARY, hover_color=UI_ACCENT):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hover = False
    
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos)
        
        if self.hover:
            self.current_color = self.hover_color
        else:
            self.current_color = self.color
        
        return self.hover != was_hover
    
    def is_clicked(self, pos):
        """Simple click detection - just check if mouse is over button"""
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Draw button background
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)
        
        # Draw text
        text_surface = font_medium.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

def draw_animated_background(surface, timer):
    """Draw animated background for menus"""
    # Draw animated background
    for y in range(0, SCREEN_HEIGHT, 5):
        color_value = 20 + int(10 * math.sin(timer * 0.01 + y * 0.01))
        color = (color_value, color_value, color_value + 20)
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
    
    # Draw some floating particles
    for i in range(20):
        x = (timer * (i % 5 + 1) * 0.5 + i * 100) % SCREEN_WIDTH
        y = (timer * (i % 3 + 1) * 0.2 + i * 50) % SCREEN_HEIGHT
        size = 2 + math.sin(timer * 0.05 + i) * 2
        
        # Make particles glow
        glow = 100 + int(50 * math.sin(timer * 0.1 + i))
        color = (glow, glow, min(255, glow + 50))
        
        pygame.draw.circle(surface, color, (int(x), int(y)), int(size))

def show_host_menu(screen, clock):
    """Show menu for hosting a game"""
    animation_timer = 0
    global CURRENT_USERNAME, CURRENT_HOSTED_ROOM
    
    # Create UI elements
    title_text = "Host Multiplayer Game"
    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 60, "Back", UI_DANGER)
    host_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60, "Host Game", UI_SUCCESS)
    
    # Input fields
    username_input = TextInput(SCREEN_WIDTH//2 - 150, 200, 300, 50, "Enter your username", font_medium)
    if CURRENT_USERNAME:
        username_input.text = CURRENT_USERNAME
        
    room_name_input = TextInput(SCREEN_WIDTH//2 - 150, 280, 300, 50, "Enter room name", font_medium)
    
    # Auto-update room name when username changes
    last_username = ""
    
    def update_room_name():
        nonlocal last_username
        if username_input.text and username_input.text != last_username:
            if not room_name_input.text or room_name_input.text == f"{last_username}'s room":
                room_name_input.text = f"{username_input.text}'s room"
            last_username = username_input.text
    
    # Map selection
    map_options = ["Random", "Sky Battle", "Forest Arena", "Castle", "Space Station"]
    selected_map = 0
    
    prev_map_button = Button(SCREEN_WIDTH//2 - 250, 360, 80, 50, "<", UI_SECONDARY)
    next_map_button = Button(SCREEN_WIDTH//2 + 170, 360, 80, 50, ">", UI_SECONDARY)
    
    # Max players selection
    max_players = 4
    
    prev_players_button = Button(SCREEN_WIDTH//2 - 250, 420, 80, 50, "<", UI_SECONDARY)
    next_players_button = Button(SCREEN_WIDTH//2 + 170, 420, 80, 50, ">", UI_SECONDARY)
    
    # Game client
    client = None
    connected = False
    hosting = False
    
    # Check if we already have an active client for this username
    def get_or_create_client():
        nonlocal client, connected, hosting, room_name_input
        
        # Check if we have a currently hosted room
        if CURRENT_HOSTED_ROOM and username_input.text in ACTIVE_CLIENTS:
            # Use existing client
            client = ACTIVE_CLIENTS[username_input.text]
            connected = client.connected
            
            # If already hosting, update UI
            if client.is_host:
                hosting = True
                room_name_input.text = CURRENT_HOSTED_ROOM
                return True
        elif username_input.text in ACTIVE_CLIENTS:
            # Use existing client
            client = ACTIVE_CLIENTS[username_input.text]
            connected = client.connected
            
            # If already hosting, update UI
            if client.is_host and client.current_room:
                hosting = True
                room_name_input.text = client.current_room
                return True
        else:
            # Create new client
            client = GameClient()
            connected = False
        
        return False
    
    # Player count display
    player_count_display = PlayerCountDisplay(SCREEN_WIDTH - 100, 50)
    
    # Chat box - positioned to avoid overlap with max players
    chat_box = ChatBox(50, 500, SCREEN_WIDTH - 100, 100)
    chat_input = TextInput(50, 610, SCREEN_WIDTH - 220, 40, "Type a message...", font_small)
    send_button = Button(SCREEN_WIDTH - 150, 610, 100, 40, "Send", UI_ACCENT)
    
    # Set up client callbacks
    def setup_callbacks():
        if not client:
            return
            
        def on_connect(data):
            nonlocal connected
            connected = True
            chat_box.add_message("System", f"Connected to server as {username_input.text}")
        
        def on_disconnect():
            nonlocal connected, hosting
            connected = False
            # Don't set hosting to false if KEEP_ROOMS_ACTIVE is True
            if not KEEP_ROOMS_ACTIVE:
                hosting = False
            chat_box.add_message("System", "Disconnected from server")
        
        def on_player_count(count):
            player_count_display.update(count)
        
        def on_player_joined(username, count):
            chat_box.add_message("System", f"{username} joined the game")
            player_count_display.update(count)
        
        def on_player_left(username, count):
            chat_box.add_message("System", f"{username} left the game")
            player_count_display.update(count)
        
        def on_room_created(room_id):
            nonlocal hosting
            hosting = True
            chat_box.add_message("System", f"Room created with ID: {room_id}")
            chat_box.add_message("System", "Your room is now available in the Browse Rooms menu")
            room_name_input.text = room_id  # Update room name with actual ID
        
        def on_chat(username, message, room_id):
            chat_box.add_message(username, message)
        
        def on_error(message):
            chat_box.add_message("Error", message)
        
        client.set_callback("on_connect", on_connect)
        client.set_callback("on_disconnect", on_disconnect)
        client.set_callback("on_player_count", on_player_count)
        client.set_callback("on_player_joined", on_player_joined)
        client.set_callback("on_player_left", on_player_left)
        client.set_callback("on_room_created", on_room_created)
        client.set_callback("on_chat", on_chat)
        client.set_callback("on_error", on_error)
    
    # Check for existing client/room
    already_hosting = get_or_create_client()
    setup_callbacks()
    
    # If already hosting, update UI
    if already_hosting:
        chat_box.add_message("System", f"Resumed hosting room: {client.current_room}")
    
    running = True
    while running:
        animation_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Scroll chat with arrow keys
                if event.key == pygame.K_UP:
                    chat_box.scroll_up()
                elif event.key == pygame.K_DOWN:
                    chat_box.scroll_down()
                
                # Send chat with Enter if chat input is active
                if event.key == pygame.K_RETURN and chat_input.active and chat_input.text:
                    if connected and client:
                        client.send_chat(chat_input.text, room_name_input.text if hosting else None)
                    chat_input.text = ""
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(mouse_pos):
                    # Save current username
                    CURRENT_USERNAME = username_input.text

                    # IMPORTANT: Save the current hosted room
                    if hosting and client and client.current_room:
                        CURRENT_HOSTED_ROOM = client.current_room

                        # Make sure the room stays active
                        for room in HOSTED_ROOMS:
                            if room["room_id"] == client.current_room:
                                room["active"] = True
                                break

                    running = False
                    
                elif host_button.is_clicked(mouse_pos) and not hosting:
                    if username_input.text:
                        # Make sure room name is set
                        if not room_name_input.text:
                            room_name_input.text = f"{username_input.text}'s room"
                        
                        # Get or create client
                        get_or_create_client()
                        setup_callbacks()
                            
                        if not connected and client:
                            # Connect to server
                            if client.connect("localhost", DEFAULT_PORT, username_input.text):
                                # Create room after connection
                                pass
                        elif client:
                            # Create room
                            client.join_room(room_name_input.text)
                            hosting = True
                    else:
                        chat_box.add_message("Error", "Please enter a username first")
                
                elif prev_map_button.is_clicked(mouse_pos):
                    selected_map = (selected_map - 1) % len(map_options)
                
                elif next_map_button.is_clicked(mouse_pos):
                    selected_map = (selected_map + 1) % len(map_options)
                
                elif prev_players_button.is_clicked(mouse_pos):
                    max_players = max(2, max_players - 1)
                
                elif next_players_button.is_clicked(mouse_pos):
                    max_players = min(6, max_players + 1)
                
                elif send_button.is_clicked(mouse_pos) and chat_input.text:
                    if connected and client:
                        client.send_chat(chat_input.text, room_name_input.text if hosting else None)
                    chat_input.text = ""
            
            # Handle text inputs
            username_input.handle_event(event)
            room_name_input.handle_event(event)
            chat_input.handle_event(event)
            
            # Update room name based on username
            update_room_name()
        
        # Update button hover states
        back_button.check_hover(mouse_pos)
        host_button.check_hover(mouse_pos)
        prev_map_button.check_hover(mouse_pos)
        next_map_button.check_hover(mouse_pos)
        prev_players_button.check_hover(mouse_pos)
        next_players_button.check_hover(mouse_pos)
        send_button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BLACK)
        draw_animated_background(screen, animation_timer)
        
        # Draw title
        title_surface = font_title.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_surface, title_rect)
        
        # Draw connection status
        if connected:
            status_text = "Connected to server"
            status_color = GREEN
        else:
            status_text = "Not connected"
            status_color = RED
        
        status_surface = font_medium.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(status_surface, status_rect)
        
        # Draw UI elements
        username_input.draw(screen)
        room_name_input.draw(screen)
        chat_box.draw(screen)
        chat_input.draw(screen)
        send_button.draw(screen)
        back_button.draw(screen)
        
        # Draw host button or hosting status
        if hosting:
            host_status = font_medium.render("Hosting Game", True, GREEN)
            host_rect = host_status.get_rect(center=(SCREEN_WIDTH - 125, SCREEN_HEIGHT - 100))
            screen.blit(host_status, host_rect)
        else:
            host_button.draw(screen)
        
        # Draw map selection
        map_label = font_medium.render("Map:", True, WHITE)
        screen.blit(map_label, (SCREEN_WIDTH//2 - 150, 360))
        
        map_value = font_medium.render(map_options[selected_map], True, GOLD)
        map_rect = map_value.get_rect(center=(SCREEN_WIDTH//2, 385))
        screen.blit(map_value, map_rect)
        
        prev_map_button.draw(screen)
        next_map_button.draw(screen)
        
        # Draw max players selection
        players_label = font_medium.render("Max Players:", True, WHITE)
        screen.blit(players_label, (SCREEN_WIDTH//2 - 150, 420))
        
        players_value = font_medium.render(str(max_players), True, GOLD)
        players_rect = players_value.get_rect(center=(SCREEN_WIDTH//2, 445))
        screen.blit(players_value, players_rect)
        
        prev_players_button.draw(screen)
        next_players_button.draw(screen)
        
        # Draw player count
        player_count_display.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Don't disconnect when going back to menu
    # if client and client.connected:
    #     client.disconnect()
    
    return None

# Room list item class
class RoomListItem:
    def __init__(self, x, y, width, height, room_data):
        self.rect = pygame.Rect(x, y, width, height)
        self.room_data = room_data
        self.hover = False
        
    def draw(self, surface, current_username=""):
        # Determine if this is the user's own room
        is_own_room = self.room_data.get("host", "") == current_username
        
        # Draw background with special styling for own rooms
        if self.hover:
            if is_own_room:
                bg_color = (80, 60, 120)  # Purple tint for own rooms when hovered
            else:
                bg_color = UI_SECONDARY
        else:
            if is_own_room:
                bg_color = (60, 40, 80)   # Darker purple for own rooms
            else:
                bg_color = UI_PRIMARY
        
        pygame.draw.rect(surface, bg_color, self.rect)
        
        # Draw border - special color for own rooms
        border_color = GOLD if is_own_room else WHITE
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Draw room info
        room_id = self.room_data.get("room_id", "Unknown")
        host = self.room_data.get("host", "Unknown")
        map_name = self.room_data.get("map", "Random")
        players = self.room_data.get("players", 0)
        max_players = self.room_data.get("max_players", 2)
        
        # Room ID with indicator for own rooms
        room_text = f"Room: {room_id}"
        if is_own_room:
            room_text += " (Your Room)"
        id_text = font_small.render(room_text, True, GOLD if is_own_room else WHITE)
        surface.blit(id_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Host
        host_text = font_small.render(f"Host: {host}", True, WHITE)
        surface.blit(host_text, (self.rect.x + 10, self.rect.y + 40))
        
        # Map
        map_text = font_small.render(f"Map: {map_name}", True, GOLD)
        surface.blit(map_text, (self.rect.x + 10, self.rect.y + 70))
        
        # Players
        players_text = font_small.render(f"Players: {players}/{max_players}", True, GREEN if players < max_players else RED)
        surface.blit(players_text, (self.rect.x + self.rect.width - 150, self.rect.y + 40))
        
        # Add helpful text for own rooms
        if is_own_room:
            help_text = font_tiny.render("Use a different username to join", True, YELLOW)
            surface.blit(help_text, (self.rect.x + self.rect.width - 200, self.rect.y + 70))
    
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos)
        return self.hover != was_hover
    
    def is_clicked(self, pos):
        """Simple click detection - just check if mouse is over room item"""
        return self.rect.collidepoint(pos)

def show_browse_rooms_menu(screen, clock):
    """Show menu for browsing available game rooms"""
    animation_timer = 0
    global CURRENT_USERNAME
    
    # Create UI elements
    title_text = "Browse Game Rooms"
    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 60, "Back", UI_DANGER)
    refresh_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60, "Refresh", UI_SUCCESS)
    
    # Username input
    username_input = TextInput(SCREEN_WIDTH//2 - 150, 100, 300, 50, "Enter your username", font_medium)
    if CURRENT_USERNAME:
        username_input.text = CURRENT_USERNAME
    
    # Game client
    client = None
    connected = False
    
    # Check if we already have an active client for this username
    def get_or_create_client():
        nonlocal client, connected
        
        if username_input.text in ACTIVE_CLIENTS:
            # Use existing client
            client = ACTIVE_CLIENTS[username_input.text]
            connected = client.connected
            return True
        else:
            # Create new client
            client = GameClient()
            connected = False
            return False
    
    # Room list variables
    dummy_rooms = []
    room_items = []
    
    # Status message
    status_message = "Enter username and connect to see available rooms"
    status_color = YELLOW
    
    # Function to refresh room list
    def refresh_room_list():
        nonlocal dummy_rooms, room_items, status_message, status_color
        
        # Start with actual hosted rooms
        dummy_rooms = []
        
        # Add any hosted rooms first (these are the real rooms)
        for room in HOSTED_ROOMS:
            if room.get("active", True):  # Only include active rooms
                dummy_rooms.append(room)
        
        # Only add dummy rooms if no real rooms exist (for testing purposes)
        if not dummy_rooms:
            dummy_rooms = [
                {
                    "room_id": "room1",
                    "host": "Player1",
                    "map": "Sky Battle",
                    "players": 1,
                    "max_players": 6
                },
                {
                    "room_id": "room2",
                    "host": "Player2",
                    "map": "Forest Arena",
                    "players": 2,
                    "max_players": 4
                }
            ]
        
        # Create room items from data
        room_items = []
        for i, room_data in enumerate(dummy_rooms):
            y_pos = 200 + i * 120
            if y_pos < SCREEN_HEIGHT - 100:  # Ensure it fits on screen
                room_items.append(RoomListItem(50, y_pos, SCREEN_WIDTH - 100, 100, room_data))
        
        if dummy_rooms:
            status_message = f"Found {len(dummy_rooms)} available room(s)"
            status_color = GREEN
        else:
            status_message = "No rooms available"
            status_color = YELLOW
    
    # Set up client callbacks
    def setup_callbacks():
        if not client:
            return
            
        def on_connect(data):
            nonlocal connected, status_message, status_color
            connected = True
            status_message = f"Connected as {username_input.text}. Requesting room list..."
            status_color = GREEN
            # Request room list
            client.get_available_rooms()
        
        def on_disconnect():
            nonlocal connected, status_message, status_color
            connected = False
            status_message = "Disconnected from server"
            status_color = RED
        
        def on_error(message):
            nonlocal status_message, status_color
            status_message = f"Error: {message}"
            status_color = RED
        
        def on_room_list(rooms):
            nonlocal dummy_rooms, room_items, status_message, status_color
            dummy_rooms = rooms
            
            # Create room items
            room_items = []
            for i, room_data in enumerate(dummy_rooms):
                y_pos = 200 + i * 120
                if y_pos < SCREEN_HEIGHT - 100:  # Ensure it fits on screen
                    room_items.append(RoomListItem(50, y_pos, SCREEN_WIDTH - 100, 100, room_data))
            
            if dummy_rooms:
                status_message = f"Found {len(dummy_rooms)} available room(s)"
                status_color = GREEN
            else:
                status_message = "No rooms available"
                status_color = YELLOW
        
        client.set_callback("on_connect", on_connect)
        client.set_callback("on_disconnect", on_disconnect)
        client.set_callback("on_error", on_error)
        client.set_callback("on_room_list", on_room_list)
    
    # Initial room list load
    refresh_room_list()
    
    running = True
    while running:
        animation_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Handle text inputs
            username_input.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(mouse_pos):
                    # Save current username
                    CURRENT_USERNAME = username_input.text
                    running = False
                
                elif refresh_button.is_clicked(mouse_pos):
                    # Save current username
                    CURRENT_USERNAME = username_input.text
                    
                    # Refresh the room list
                    refresh_room_list()
                
                # Check room item clicks
                else:
                    for item in room_items:
                        if item.is_clicked(mouse_pos):
                            # Join the selected room
                            room_id = item.room_data.get("room_id")
                            if room_id:
                                # Save current username
                                CURRENT_USERNAME = username_input.text
                                
                                # Check if this is our own room with the same username
                                is_same_user_same_room = False
                                for room in HOSTED_ROOMS:
                                    if room["room_id"] == room_id and room["host"] == username_input.text:
                                        is_same_user_same_room = True
                                        break
                                
                                if is_same_user_same_room:
                                    status_message = "Cannot join your own room with the same username. Try a different username to join your own room."
                                    status_color = RED
                                    break
                                
                                # Store the room ID and username for the join menu
                                selected_room = {
                                    "room_id": room_id,
                                    "username": username_input.text if username_input.text else "Player",
                                    "host": item.room_data.get("host"),
                                    "map": item.room_data.get("map")
                                }
                                
                                # Show join menu with pre-filled room ID
                                show_join_menu(screen, clock, selected_room)
                                
                                # Refresh the room list after returning
                                refresh_room_list()
                            break
        
        # Update button hover states
        back_button.check_hover(mouse_pos)
        refresh_button.check_hover(mouse_pos)
        
        # Update room item hover states
        for item in room_items:
            item.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BLACK)
        draw_animated_background(screen, animation_timer)
        
        # Draw title
        title_surface = font_title.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
        screen.blit(title_surface, title_rect)
        
        # Draw status message
        status_surface = font_medium.render(status_message, True, status_color)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, 170))
        screen.blit(status_surface, status_rect)
        
        # Draw UI elements
        username_input.draw(screen)
        back_button.draw(screen)
        refresh_button.draw(screen)
        
        # Draw room items
        for item in room_items:
            item.draw(screen, username_input.text)
        
        # Draw "No rooms" message if no rooms
        if not room_items:
            no_rooms_text = font_medium.render("No game rooms available. Try refreshing or hosting your own game.", True, LIGHT_GRAY)
            no_rooms_rect = no_rooms_text.get_rect(center=(SCREEN_WIDTH//2, 300))
            screen.blit(no_rooms_text, no_rooms_rect)
        
        # Draw helpful instructions
        instructions = [
            "Tip: You can join your own hosted rooms by using a different username",
            "Your hosted rooms are highlighted in gold"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_text = font_tiny.render(instruction, True, LIGHT_GRAY)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 120 + i * 20))
            screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    return None
def show_join_menu(screen, clock, selected_room=None):
    """Show menu for joining a game"""
    animation_timer = 0
    global CURRENT_USERNAME
    
    # Create UI elements
    title_text = "Join Multiplayer Game"
    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 60, "Back", UI_DANGER)
    join_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60, "Join Game", UI_SUCCESS)
    
    # Input fields - pre-fill if selected_room is provided
    username_text = selected_room.get("username", "") if selected_room else ""
    room_id_text = selected_room.get("room_id", "") if selected_room else ""
    
    username_input = TextInput(SCREEN_WIDTH//2 - 150, 200, 300, 50, "Enter your username", font_medium)
    if username_text:
        username_input.text = username_text
    elif CURRENT_USERNAME:
        username_input.text = CURRENT_USERNAME
    
    server_input = TextInput(SCREEN_WIDTH//2 - 150, 280, 300, 50, "Enter server IP", font_medium)
    server_input.text = "localhost"  # Default to localhost
    
    room_input = TextInput(SCREEN_WIDTH//2 - 150, 360, 300, 50, "Enter room ID", font_medium)
    if room_id_text:
        room_input.text = room_id_text
    
    # Game client
    client = GameClient()
    connected = False
    joined_room = False
    
    # Player count display
    player_count_display = PlayerCountDisplay(SCREEN_WIDTH - 100, 50)
    
    # Chat box
    chat_box = ChatBox(50, 430, SCREEN_WIDTH - 100, 200)
    chat_input = TextInput(50, 650, SCREEN_WIDTH - 220, 50, "Type a message...", font_small)
    send_button = Button(SCREEN_WIDTH - 150, 650, 100, 50, "Send", UI_ACCENT)
    
    # Set up client callbacks
    def on_connect(data):
        nonlocal connected
        connected = True
        chat_box.add_message("System", f"Connected to server as {username_input.text}")
        
        # Auto-join room if selected
        if room_input.text and selected_room:
            client.join_room(room_input.text)
    
    def on_disconnect():
        nonlocal connected
        connected = False
        chat_box.add_message("System", "Disconnected from server")
    
    def on_player_count(count):
        player_count_display.update(count)
    
    def on_player_joined(username, count):
        chat_box.add_message("System", f"{username} joined the game")
        player_count_display.update(count)
    
    def on_player_left(username, count):
        chat_box.add_message("System", f"{username} left the game")
        player_count_display.update(count)
    
    def on_room_joined(room_id, players, map_name, message):
        nonlocal joined_room
        joined_room = True
        chat_box.add_message("System", f"Joined room {room_id}")
        chat_box.add_message("System", f"Players in room: {', '.join(players)}")
        chat_box.add_message("System", f"Map: {map_name}")
    
    def on_chat(username, message, room_id):
        chat_box.add_message(username, message)
    
    def on_error(message):
        chat_box.add_message("Error", message)
    
    client.set_callback("on_connect", on_connect)
    client.set_callback("on_disconnect", on_disconnect)
    client.set_callback("on_player_count", on_player_count)
    client.set_callback("on_player_joined", on_player_joined)
    client.set_callback("on_player_left", on_player_left)
    client.set_callback("on_room_joined", on_room_joined)
    client.set_callback("on_chat", on_chat)
    client.set_callback("on_error", on_error)
    
    # If we have a selected room, show some info about it
    selected_room_info = None
    if selected_room:
        selected_room_info = {
            "host": selected_room.get("host", "Unknown"),
            "map": selected_room.get("map", "Random")
        }
    
    running = True
    while running:
        animation_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Scroll chat with arrow keys
                if event.key == pygame.K_UP:
                    chat_box.scroll_up()
                elif event.key == pygame.K_DOWN:
                    chat_box.scroll_down()
                
                # Send chat with Enter if chat input is active
                if event.key == pygame.K_RETURN and chat_input.active and chat_input.text:
                    if connected:
                        client.send_chat(chat_input.text, room_input.text if joined_room else None)
                    chat_input.text = ""
            
            # Handle text inputs
            username_input.handle_event(event)
            server_input.handle_event(event)
            room_input.handle_event(event)
            chat_input.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_clicked(mouse_pos):
                    running = False
                
                elif join_button.is_clicked(mouse_pos) and not joined_room:
                    if username_input.text and server_input.text and room_input.text:
                        if not connected:
                            # Connect to server
                            if client.connect(server_input.text, DEFAULT_PORT, username_input.text):
                                # Join will happen after connection
                                pass
                        else:
                            # Join room
                            client.join_room(room_input.text)
                
                elif send_button.is_clicked(mouse_pos) and chat_input.text:
                    if connected:
                        client.send_chat(chat_input.text, room_input.text if joined_room else None)
                    chat_input.text = ""
        
        # If connected but not joined room, try to join
        if connected and not joined_room and room_input.text:
            client.join_room(room_input.text)
        
        # Update button hover states
        back_button.check_hover(mouse_pos)
        join_button.check_hover(mouse_pos)
        send_button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BLACK)
        draw_animated_background(screen, animation_timer)
        
        # Draw title
        title_surface = font_title.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_surface, title_rect)
        
        # Draw connection status
        if connected:
            status_text = f"Connected to {server_input.text}"
            status_color = GREEN
        else:
            status_text = "Not connected"
            status_color = RED
        
        status_surface = font_medium.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(status_surface, status_rect)
        
        # Draw selected room info if available
        if selected_room_info and not joined_room:
            info_text = f"Selected Room - Host: {selected_room_info['host']} | Map: {selected_room_info['map']}"
            info_surface = font_small.render(info_text, True, GOLD)
            info_rect = info_surface.get_rect(center=(SCREEN_WIDTH//2, 420))
            screen.blit(info_surface, info_rect)
        
        # Draw UI elements
        username_input.draw(screen)
        server_input.draw(screen)
        room_input.draw(screen)
        chat_box.draw(screen)
        chat_input.draw(screen)
        send_button.draw(screen)
        back_button.draw(screen)
        join_button.draw(screen)
        
        # Draw player count
        player_count_display.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Clean up
    if client.connected:
        client.disconnect()
    
    return None

def show_multiplayer_menu(screen, clock):
    """Show multiplayer menu"""
    animation_timer = 0
    
    # Create buttons
    button_width = 300
    button_height = 80
    button_x = SCREEN_WIDTH//2 - button_width//2
    
    host_button = Button(button_x, 200, button_width, button_height, "Host Game", UI_PRIMARY, UI_ACCENT)
    browse_button = Button(button_x, 300, button_width, button_height, "Browse Rooms", UI_PRIMARY, UI_ACCENT)
    join_button = Button(button_x, 400, button_width, button_height, "Join Game", UI_PRIMARY, UI_ACCENT)
    back_button = Button(button_x, 500, button_width, button_height, "Back to Main Menu", UI_DANGER, UI_DANGER)
    
    # Create player count display
    player_count = PlayerCountDisplay(SCREEN_WIDTH - 100, 50)
    
    # Display hosted rooms count
    hosted_rooms_count = len(HOSTED_ROOMS)
    
    running = True
    while running:
        animation_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if host_button.is_clicked(mouse_pos):
                    show_host_menu(screen, clock)
                    # Update hosted rooms count after returning from host menu
                    hosted_rooms_count = len(HOSTED_ROOMS)
                
                elif browse_button.is_clicked(mouse_pos):
                    show_browse_rooms_menu(screen, clock)
                
                elif join_button.is_clicked(mouse_pos):
                    show_join_menu(screen, clock)
                
                elif back_button.is_clicked(mouse_pos):
                    running = False
        
        # Update button hover states
        host_button.check_hover(mouse_pos)
        browse_button.check_hover(mouse_pos)
        join_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
        
        # Draw everything
        screen.fill(BLACK)
        draw_animated_background(screen, animation_timer)
        
        # Draw title
        title_text = "Multiplayer Mode"
        title_surface = font_title.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_text = "Play with friends online!"
        subtitle_surface = font_medium.render(subtitle_text, True, GOLD)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw buttons
        host_button.draw(screen)
        browse_button.draw(screen)
        join_button.draw(screen)
        back_button.draw(screen)
        
        # Draw player count
        player_count.draw(screen)
        
        # Draw hosted rooms info
        if hosted_rooms_count > 0:
            rooms_text = f"You are hosting {hosted_rooms_count} room(s)"
            rooms_surface = font_small.render(rooms_text, True, GREEN)
            rooms_rect = rooms_surface.get_rect(center=(SCREEN_WIDTH//2, 580))
            screen.blit(rooms_surface, rooms_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    return None
