#file based on snither example
import pygame as pg

# Game path should already be added by cartridge loader
from Games.Meteors.main import Meteors

class ConsoleEntry:
    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players

        Meteors(self.display_surf, self.console_update, self.get_num_players)