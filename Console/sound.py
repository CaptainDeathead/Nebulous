import pygame as pg
import numpy as np

def generate_square_wave(frequency: int, duration: float = 1.0, volume: float = 0.5, sample_rate: int = 44100) -> pg.Sound:
    t = np.arange(int(sample_rate * duration))
    
    buffer = np.sign(np.sin(2 * np.pi * t * frequency / sample_rate)) * volume
    buffer = np.int16(buffer * 32767)  # Convert to 16-bit PCM format

    return pg.mixer.Sound(buffer)

def generate_sine_wave(frequency: int, duration: float = 1.0, volume: float = 0.5, sample_rate: int = 44100) -> pg.mixer.Sound:
    t = np.arange(int(sample_rate * duration)) / sample_rate

    buffer = np.sin(2 * np.pi * frequency * t) * volume
    buffer = np.int16(buffer * 32767)  # Convert to 16-bit PCM format
    
    return pg.mixer.Sound(buffer)