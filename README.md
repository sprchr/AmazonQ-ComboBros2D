🎮 Combo Bros 2D

Combo Bros 2D is a fast-paced, retro-style 2D fighting game inspired by Super Smash Bros. Built with Pygame, it features vibrant pixel art characters, AI opponents, procedural stages, local multiplayer, and special attacks — all crafted for an action-packed experience.

🧠 Features
Retro Pixel Art Fighters: Choose from a roster of characters, each with unique colors, powers, and visual styles.

Single & Local Multiplayer: Battle against a friend or challenge AI bots with adjustable difficulty.

AI Combat: Intelligent opponents that change behavior based on difficulty (Easy to Insane).

Special Attacks & Knockback: Use character-specific specials like Blaze’s Fire Nova or Nimbus’s Cloud Dash.

Procedural Sky Maps: Dynamic platform generation for unique arenas each match.

Stylized Effects: Includes custom animations, particles (fire, leaves, clouds), and screen overlays.

Game Modes: Character selection, difficulty selection, and online multiplayer (menu interface provided).

Audio Support: Background music and SFX (with graceful fallback if audio fails).

🕹️ Controls
Player 1:
A / D: Move left/right

W: Jump

F / N: Attack

G / M: Special attack

Player 2 (Local Multiplayer):
← / →: Move left/right

↑: Jump

, / N: Attack

. / M: Special attack

🔧 Installation
Clone this repository:




git clone https://github.com/yourusername/combobros2d.git
cd combobros2d
Install dependencies:



pip install pygame
Run the game:



python main_game.py
Note: Game runs in full-screen. Press ESC to return to menu or quit.

📁 Project Structure



📁 combobros2d/
├── main_game.py               # Main game logic and game loop
├── character_select.py        # Character selection menu
├── difficulty_options.py      # Difficulty selector
├── map_generator.py           # Sky-themed procedural map generation
├── multiplayer.py             # Multiplayer menu (UI only)
├── assets/                    # Audio and image files (e.g., attack.wav, jump.wav)
🔊 Assets
Place your .wav sound effects and .mp3 background music into the project folder:

jump.wav, attack.wav, hit.wav, special.wav

menu_music.mp3, battle_music.mp3

If these are missing, the game will still run without audio.
