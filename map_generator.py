import random
import pygame

def generate_sky_map(screen_width, screen_height, platform_height, ground_y, difficulty="Normal"):
    """
    Generate a random sky map with platforms
    
    Args:
        screen_width: Width of the screen
        screen_height: Height of the screen
        platform_height: Height of each platform
        ground_y: Y position of the ground
        difficulty: Game difficulty affecting platform generation
        
    Returns:
        List of platform dictionaries with x, y, width, and color
    """
    platforms = []
    
    # Map types
    map_types = [
        "floating_islands",
        "stairway",
        "symmetrical",
        "scattered",
        "tower",
        "arena"
    ]
    
    # Select a random map type
    map_type = random.choice(map_types)
    
    # Colors for platforms
    platform_colors = [
        (105, 105, 105),  # Gray
        (139, 69, 19),    # Brown
        (46, 139, 87),    # Sea Green
        (70, 130, 180),   # Steel Blue
        (205, 133, 63),   # Peru
        (160, 82, 45),    # Sienna
    ]
    
    # Adjust platform count based on difficulty
    if difficulty == "Easy":
        platform_count = random.randint(3, 5)
    elif difficulty == "Normal":
        platform_count = random.randint(4, 7)
    elif difficulty == "Hard":
        platform_count = random.randint(5, 8)
    else:  # Insane
        platform_count = random.randint(6, 10)
    
    # Generate platforms based on map type
    if map_type == "floating_islands":
        # Create several floating islands
        for i in range(platform_count):
            width = random.randint(100, 250)
            x = random.randint(50, screen_width - width - 50)
            y = random.randint(ground_y - 400, ground_y - 100)
            color = random.choice(platform_colors)
            platforms.append({"x": x, "y": y, "width": width, "color": color})
    
    elif map_type == "stairway":
        # Create a stairway pattern
        step_width = random.randint(100, 200)
        start_x = random.randint(50, screen_width // 2 - step_width)
        start_y = ground_y - 100
        
        for i in range(platform_count):
            x = start_x + (i * step_width // 2)
            y = start_y - (i * 70)
            width = step_width
            color = random.choice(platform_colors)
            platforms.append({"x": x, "y": y, "width": width, "color": color})
            
            # Add a mirrored stairway on the right side
            mirror_x = screen_width - x - width
            platforms.append({"x": mirror_x, "y": y, "width": width, "color": color})
    
    elif map_type == "symmetrical":
        # Create a symmetrical layout
        center_platform = {
            "x": screen_width // 2 - 200,
            "y": ground_y - 200,
            "width": 400,
            "color": random.choice(platform_colors)
        }
        platforms.append(center_platform)
        
        for i in range((platform_count - 1) // 2):
            width = random.randint(100, 200)
            y_offset = random.randint(100, 300)
            x_offset = random.randint(50, 300)
            
            # Left platform
            left_platform = {
                "x": center_platform["x"] - width - x_offset,
                "y": center_platform["y"] - y_offset,
                "width": width,
                "color": random.choice(platform_colors)
            }
            platforms.append(left_platform)
            
            # Right platform (mirrored)
            right_x = screen_width - left_platform["x"] - width
            platforms.append({
                "x": right_x,
                "y": left_platform["y"],
                "width": width,
                "color": left_platform["color"]
            })
    
    elif map_type == "scattered":
        # Create randomly scattered platforms
        for i in range(platform_count):
            width = random.randint(80, 200)
            x = random.randint(50, screen_width - width - 50)
            y = random.randint(ground_y - 400, ground_y - 100)
            color = random.choice(platform_colors)
            platforms.append({"x": x, "y": y, "width": width, "color": color})
    
    elif map_type == "tower":
        # Create a tower-like structure
        center_x = screen_width // 2
        platform_width = 400
        
        for i in range(platform_count):
            width = platform_width - (i * 30)
            x = center_x - width // 2
            y = ground_y - 100 - (i * 80)
            color = random.choice(platform_colors)
            platforms.append({"x": x, "y": y, "width": width, "color": color})
    
    elif map_type == "arena":
        # Create an arena-like structure
        main_platform = {
            "x": screen_width // 2 - 300,
            "y": ground_y - 200,
            "width": 600,
            "color": random.choice(platform_colors)
        }
        platforms.append(main_platform)
        
        # Add side platforms
        left_platform = {
            "x": 100,
            "y": ground_y - 300,
            "width": 150,
            "color": random.choice(platform_colors)
        }
        platforms.append(left_platform)
        
        right_platform = {
            "x": screen_width - 250,
            "y": ground_y - 300,
            "width": 150,
            "color": random.choice(platform_colors)
        }
        platforms.append(right_platform)
        
        # Add top platform
        top_platform = {
            "x": screen_width // 2 - 100,
            "y": ground_y - 400,
            "width": 200,
            "color": random.choice(platform_colors)
        }
        platforms.append(top_platform)
        
        # Add more random platforms if needed
        for i in range(platform_count - 4):
            width = random.randint(80, 150)
            x = random.randint(50, screen_width - width - 50)
            y = random.randint(ground_y - 450, ground_y - 250)
            color = random.choice(platform_colors)
            platforms.append({"x": x, "y": y, "width": width, "color": color})
    
    # Always add a ground platform
    ground_platform = {
        "x": 0,
        "y": ground_y,
        "width": screen_width,
        "color": (64, 64, 64)  # Dark gray
    }
    platforms.append(ground_platform)
    
    return platforms, map_type

def create_platform_objects(platforms, Platform):
    """
    Convert platform dictionaries to Platform objects
    
    Args:
        platforms: List of platform dictionaries
        Platform: Platform class to instantiate
        
    Returns:
        List of Platform objects
    """
    platform_objects = []
    
    for platform in platforms:
        platform_obj = Platform(
            platform["x"],
            platform["y"],
            platform["width"],
            color=platform["color"]
        )
        platform_objects.append(platform_obj)
    
    return platform_objects

def get_map_name(map_type):
    """
    Get a fancy name for the map type
    
    Args:
        map_type: The map type string
        
    Returns:
        A fancy name for the map
    """
    map_names = {
        "floating_islands": [
            "Celestial Islands", 
            "Sky Archipelago", 
            "Drifting Sanctuaries"
        ],
        "stairway": [
            "Stairway to Heaven", 
            "Ascending Path", 
            "Skyward Steps"
        ],
        "symmetrical": [
            "Mirror Realm", 
            "Balanced Battleground", 
            "Equilibrium"
        ],
        "scattered": [
            "Chaotic Skies", 
            "Scattered Fragments", 
            "Disarray Heights"
        ],
        "tower": [
            "Sky Tower", 
            "Ascending Spire", 
            "Vertical Challenge"
        ],
        "arena": [
            "Cloud Colosseum", 
            "Sky Arena", 
            "Aerial Battleground"
        ]
    }
    
    return random.choice(map_names.get(map_type, ["Sky Battle"]))
