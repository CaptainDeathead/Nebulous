#file based on snither example
import pygame as pg

from subprocess import run
from threading import Thread
from time import sleep

from typing import List

class ConsoleEntry:
    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List) -> None:
        self.console_update = console_update
        self.controllers = controllers

        self.update_thread = Thread(target=self.update, daemon=True)
        self.update_thread.start()

        self.set_fceux_fullscreen()
        
        run(["fceux", "/tmp/Games/NESTetris/game.nes"], check=True)

    def set_fceux_fullscreen(self) -> None:
        with open("/home/consoleuser/.fceux/fceux.cfg", "r+") as f:
            config = f.read()
            config.replace("SDL.Fullscreen = 0", "SDL.Fullscreen = 1")
            f.write(config)

    def update(self) -> None:
        while 1:
            for controller in self.controllers:
                for event in controller.event.get():
                    pass

            self.console_update()
            sleep(0.01)
