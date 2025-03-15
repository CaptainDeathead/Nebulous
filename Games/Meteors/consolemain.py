#file based on snither example
import pygame as pg

# Game path should already be added by cartridge loader
from Games.Meteors.main import Meteors

from typing import List

class ConsoleEntry:
    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List) -> None:
        Meteors(display_surf, console_update, get_num_players, controllers)