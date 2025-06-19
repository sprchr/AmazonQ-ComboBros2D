import pygame
import sys
import math

# Maximum frame rate
MAX_FPS = 60  # Reduced from 240 to 60 for better game speed

def show_difficulty_options(screen, font_title, font_medium, font_small, font_tiny, 
                           BLACK, WHITE, GOLD, GRAY, LIGHT_GRAY, 
                           UI_PRIMARY, UI_SECONDARY, UI_ACCENT, UI_SUCCESS, UI_WARNING, UI_DANGER,
                           SCREEN_WIDTH, SCREEN_HEIGHT, Button, clock, current_difficulty="Normal"):
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
    
    # Clear all events before starting
    pygame.event.clear()
    
    running = True
    while running:
        animation_timer += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Reset button clicked states
        easy_button.clicked = False
        normal_button.clicked = False
        hard_button.clicked = False
        insane_button.clicked = False
        back_button.clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                mouse_pos = event.pos  # Get position from event for accuracy
                
                if easy_button.rect.collidepoint(mouse_pos):
                    current_difficulty = "Easy"
                    easy_button.current_color = UI_SUCCESS
                    normal_button.current_color = UI_PRIMARY
                    hard_button.current_color = UI_PRIMARY
                    insane_button.current_color = UI_PRIMARY
                
                elif normal_button.rect.collidepoint(mouse_pos):
                    current_difficulty = "Normal"
                    easy_button.current_color = UI_PRIMARY
                    normal_button.current_color = UI_ACCENT
                    hard_button.current_color = UI_PRIMARY
                    insane_button.current_color = UI_PRIMARY
                
                elif hard_button.rect.collidepoint(mouse_pos):
                    current_difficulty = "Hard"
                    easy_button.current_color = UI_PRIMARY
                    normal_button.current_color = UI_PRIMARY
                    hard_button.current_color = UI_WARNING
                    insane_button.current_color = UI_PRIMARY
                
                elif insane_button.rect.collidepoint(mouse_pos):
                    current_difficulty = "Insane"
                    easy_button.current_color = UI_PRIMARY
                    normal_button.current_color = UI_PRIMARY
                    hard_button.current_color = UI_PRIMARY
                    insane_button.current_color = UI_DANGER
                
                elif back_button.rect.collidepoint(mouse_pos):
                    # Clear events before returning
                    pygame.event.clear()
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
