import pygame as pg
import random
import logging

from Controllers.controller import Controller
from Controllers.controller_manager import ControllerManager
from cartridge_loader import CartridgeLoader
from time import sleep

FONTS_PATH = "./UI/Fonts"

class Console:
    NUM_CONTROLLER_PORTS = 4
    TARGET_FPS = 60

    def __init__(self) -> None:
        """
        Steps to initialize console:
        1. Initialize controllers and controller polling
        2. Initialize display and screen
        3. Load into blank console interface
        4. Initialize cartridge loading
        """

        self.init = False

        logging.info("Welcome from the console!!!")

        self.init_controllers()
        self.init_display()
        self.init_menu_interface()
        self.init_cartridges()

        self.init = True
        logging.info("Console startup complete!")

        # TODO: THIS IS JUST FOR TESTING
        self.load_cartidge()

        self.main()

    def init_controllers(self) -> None:
        logging.info("Initializing controllers...")

        self.controller_manager = ControllerManager()

    def init_display(self) -> None:
        logging.info("Initializing display...")

        pg.init()
        pg.mixer.init(size=32)

        self.pygame_info = pg.display.Info()
        self.WIDTH = self.pygame_info.current_w
        self.HEIGHT = self.pygame_info.current_h

        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.FULLSCREEN | pg.DOUBLEBUF | pg.HWSURFACE)
        self.clock = pg.time.Clock()

    def init_menu_interface(self) -> None:
        logging.info("Initializing menu interface...")

        font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 30)

        self.enter_cartridge_surf = font.render("Enter game cartridge...", True, (255, 255, 255))
        self.enter_cartridge_rect = pg.Rect(self.WIDTH // 2 - self.enter_cartridge_surf.width // 2, self.HEIGHT // 2 - self.enter_cartridge_surf.height // 2, self.enter_cartridge_surf.width, self.enter_cartridge_surf.height)
        self.enter_cartridge_vel = [random.choice([3, -3]), random.choice([3, -3])]

    def init_cartridges(self) -> None:
        logging.info("Initializing cartridges...")

        self.cartridge_loaded = False

    def load_cartidge(self) -> None:
        CartridgeLoader(self.on_title_launch).load_cartridge()

    def main(self) -> None:
        while not self.cartridge_loaded:
            self.delta_time = self.clock.tick(self.TARGET_FPS)
            self.screen.fill((0, 0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pass

            self.enter_cartridge_rect = self.enter_cartridge_rect.move(self.enter_cartridge_vel[0], self.enter_cartridge_vel[1])

            # Bounce of walls
            if self.enter_cartridge_rect.x <= 0:
                self.enter_cartridge_rect = pg.Rect(0, self.enter_cartridge_rect.y, self.enter_cartridge_rect.w, self.enter_cartridge_rect.h)
                self.enter_cartridge_vel[0] *= -1

            elif self.enter_cartridge_rect.x + self.enter_cartridge_rect.w >= self.WIDTH:
                self.enter_cartridge_rect = pg.Rect(self.WIDTH - self.enter_cartridge_rect.w, self.enter_cartridge_rect.y, self.enter_cartridge_rect.w, self.enter_cartridge_rect.h)
                self.enter_cartridge_vel[0] *= -1

            if self.enter_cartridge_rect.y <= 0:
                self.enter_cartridge_rect = pg.Rect(self.enter_cartridge_rect.x, 0, self.enter_cartridge_rect.w, self.enter_cartridge_rect.h)
                self.enter_cartridge_vel[1] *= -1

            elif self.enter_cartridge_rect.y + self.enter_cartridge_rect.h >= self.HEIGHT:
                self.enter_cartridge_rect = pg.Rect(self.enter_cartridge_rect.x, self.HEIGHT - self.enter_cartridge_rect.h, self.enter_cartridge_rect.w, self.enter_cartridge_rect.h)
                self.enter_cartridge_vel[1] *= -1

            self.screen.blit(self.enter_cartridge_surf, self.enter_cartridge_rect)

            pg.display.flip()

    def update(self) -> None:
        self.controller_manager.update()

    def on_title_launch(self, ConsoleEntry: object) -> None:
        while not self.init:
            sleep(0.1)

        self.cartridge_loaded = True

        ConsoleEntry(self.screen, self.update, self.controller_manager.get_num_players, self.controller_manager.controllers)

if __name__ == "__main__":
    # Where it all begins...
    console = Console()