import pygame
import numpy as np
import os
import wave
import struct

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Function to generate a simple sound effect
def generate_sound(freq, duration, volume=0.5, fade=True):
    # Generate time array
    sample_rate = 44100
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    
    # Generate sine wave
    wave_data = np.sin(2 * np.pi * freq * t)
    
    # Apply fade in/out if requested
    if fade:
        fade_duration = min(0.1, duration / 4)
        fade_samples = int(fade_duration * sample_rate)
        
        # Apply fade in
        fade_in = np.linspace(0, 1, fade_samples)
        wave_data[:fade_samples] *= fade_in
        
        # Apply fade out
        fade_out = np.linspace(1, 0, fade_samples)
        wave_data[-fade_samples:] *= fade_out
    
    # Apply volume
    wave_data *= volume
    
    return wave_data, sample_rate

# Function to save a numpy array as a WAV file
def save_wav(filename, data, sample_rate):
    # Scale to 16-bit range and convert to integers
    scaled = np.int16(data * 32767)
    
    # Open WAV file for writing
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes = 16 bits
        wav_file.setframerate(sample_rate)
        
        # Write frames
        wav_file.writeframes(scaled.tobytes())

# Generate and save sound effects
def generate_and_save_sounds():
    # Jump sound (ascending tone)
    jump_data, sr = generate_sound(440, 0.3, 0.4)
    save_wav("jump.wav", jump_data, sr)
    
    # Attack sound (short burst)
    attack_data, sr = generate_sound(220, 0.2, 0.6)
    save_wav("attack.wav", attack_data, sr)
    
    # Hit sound (descending tone)
    hit_data, sr = generate_sound(880, 0.4, 0.7)
    save_wav("hit.wav", hit_data, sr)
    
    # Special sound (complex tone)
    sample_rate = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    special_data = np.sin(2 * np.pi * 330 * t) * 0.5 + np.sin(2 * np.pi * 660 * t) * 0.3
    special_data *= np.linspace(1, 0.2, len(special_data))  # Apply envelope
    save_wav("special.wav", special_data, sample_rate)

if __name__ == "__main__":
    # Change to the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Generate and save sounds
    generate_and_save_sounds()
    
    print("Sound effects generated successfully!")
