# Room list item class
class RoomListItem:
    def __init__(self, x, y, width, height, room_data):
        self.rect = pygame.Rect(x, y, width, height)
        self.room_data = room_data
        self.hover = False
        self.clicked = False
        
    def draw(self, surface):
        # Draw background
        bg_color = UI_SECONDARY if self.hover else UI_PRIMARY
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        
        # Draw room info
        room_id = self.room_data.get("room_id", "Unknown")
        host = self.room_data.get("host", "Unknown")
        map_name = self.room_data.get("map", "Random")
        players = self.room_data.get("players", 0)
        max_players = self.room_data.get("max_players", 2)
        
        # Room ID
        id_text = font_small.render(f"Room: {room_id}", True, WHITE)
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
    
    def check_hover(self, pos):
        was_hover = self.hover
        self.hover = self.rect.collidepoint(pos)
        return self.hover != was_hover
    
    def is_clicked(self, pos, mouse_pressed):
        if self.rect.collidepoint(pos) and mouse_pressed and not self.clicked:
            self.clicked = True
            return True
        elif not mouse_pressed:
            self.clicked = False
        return False

def show_browse_rooms_menu(screen, clock):
    """Show menu for browsing available game rooms"""
    animation_timer = 0
    
    # Create UI elements
    title_text = "Browse Game Rooms"
    back_button = Button(50, SCREEN_HEIGHT - 80, 150, 60, "Back", UI_DANGER)
    refresh_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60, "Refresh", UI_SUCCESS)
    
    # Username input
    username_input = TextInput(SCREEN_WIDTH//2 - 150, 100, 300, 50, "Enter your username", font_medium)
    
    # Game client
    client = GameClient()
    connected = False
    
    # Room list
    room_list = []
    room_items = []
    
    # Status message
    status_message = "Enter username and connect to see available rooms"
    status_color = YELLOW
    
    # Set up client callbacks
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
        nonlocal room_list, room_items, status_message, status_color
        room_list = rooms
        
        # Create room items
        room_items = []
        for i, room_data in enumerate(room_list):
            y_pos = 200 + i * 120
            if y_pos < SCREEN_HEIGHT - 100:  # Ensure it fits on screen
                room_items.append(RoomListItem(50, y_pos, SCREEN_WIDTH - 100, 100, room_data))
        
        if room_list:
            status_message = f"Found {len(room_list)} available room(s)"
            status_color = GREEN
        else:
            status_message = "No rooms available"
            status_color = YELLOW
    
    client.set_callback("on_connect", on_connect)
    client.set_callback("on_disconnect", on_disconnect)
    client.set_callback("on_error", on_error)
    client.set_callback("on_room_list", on_room_list)
    
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
                if back_button.is_clicked(mouse_pos, True):
                    running = False
                
                if refresh_button.is_clicked(mouse_pos, True):
                    if connected:
                        status_message = "Refreshing room list..."
                        status_color = YELLOW
                        client.get_available_rooms()
                    elif username_input.text:
                        # Connect to server
                        status_message = "Connecting to server..."
                        status_color = YELLOW
                        if client.connect("localhost", DEFAULT_PORT, username_input.text):
                            # Connection callback will request room list
                            pass
                        else:
                            status_message = "Failed to connect to server"
                            status_color = RED
                    else:
                        status_message = "Please enter a username first"
                        status_color = RED
                
                # Check room item clicks
                for item in room_items:
                    if item.is_clicked(mouse_pos, True):
                        # Join the selected room
                        room_id = item.room_data.get("room_id")
                        if room_id:
                            # Store the room ID and username for the join menu
                            selected_room = {
                                "room_id": room_id,
                                "username": username_input.text,
                                "host": item.room_data.get("host"),
                                "map": item.room_data.get("map")
                            }
                            
                            # Clean up
                            if client.connected:
                                client.disconnect()
                            
                            # Show join menu with pre-filled room ID
                            show_join_menu(screen, clock, selected_room)
                            
                            # Reconnect and refresh room list
                            if username_input.text:
                                if client.connect("localhost", DEFAULT_PORT, username_input.text):
                                    # Connection callback will request room list
                                    pass
        
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
            item.draw(screen)
        
        # Draw "No rooms" message if connected but no rooms
        if connected and not room_items:
            no_rooms_text = font_medium.render("No game rooms available. Try refreshing or hosting your own game.", True, LIGHT_GRAY)
            no_rooms_rect = no_rooms_text.get_rect(center=(SCREEN_WIDTH//2, 300))
            screen.blit(no_rooms_text, no_rooms_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    # Clean up
    if client.connected:
        client.disconnect()
    
    return None
def show_join_menu(screen, clock, selected_room=None):
    """Show menu for joining a game"""
    animation_timer = 0
    
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
                if back_button.is_clicked(mouse_pos, True):
                    running = False
                
                if join_button.is_clicked(mouse_pos, True) and not joined_room:
                    if username_input.text and server_input.text and room_input.text:
                        if not connected:
                            # Connect to server
                            if client.connect(server_input.text, DEFAULT_PORT, username_input.text):
                                # Join will happen after connection
                                pass
                        else:
                            # Join room
                            client.join_room(room_input.text)
                
                if send_button.is_clicked(mouse_pos, True) and chat_input.text:
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
                if host_button.is_clicked(mouse_pos, True):
                    show_host_menu(screen, clock)
                
                if browse_button.is_clicked(mouse_pos, True):
                    show_browse_rooms_menu(screen, clock)
                
                if join_button.is_clicked(mouse_pos, True):
                    show_join_menu(screen, clock)
                
                if back_button.is_clicked(mouse_pos, True):
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
        
        pygame.display.flip()
        clock.tick(60)
    
    return None
