import pygame as pg
import random
import logging

from Controllers.controller import Controller
from Controllers.controller_manager import ControllerManager
from cartridge_loader import CartridgeLoader
from time import sleep, time
from threading import Thread
from sys import argv

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

FONTS_PATH = "./UI/Fonts"

class Console:
    NUM_CONTROLLER_PORTS = 4
    TARGET_FPS = 60
    TESTING = False

    def __init__(self, testing: bool = False) -> None:
        """
        Steps to initialize console:
        1. Initialize controllers and controller polling
        2. Initialize display and screen
        3. Load into blank console interface
        4. Initialize cartridge loading
        """

        self.init = False
        self.TESTING = testing

        logging.info("Welcome from the console!!!")

        self.init_controllers()
        self.init_display()
        self.init_menu_interface()
        self.init_cartridges()

        self.last_cartridge_update_check = 0
        self.cartridge_check_thread = Thread(target=self.check_cartridge)
        self.cartridge_check_thread.start()

        self.init = True
        logging.info("Console startup complete!")

        # TODO: THIS IS JUST FOR TESTING
        if self.TESTING or 1: self.load_cartidge()

        self.main()

    def init_controllers(self) -> None:
        logging.info("Initializing controllers...")

        self.controller_manager = ControllerManager(testing=self.TESTING)

    def init_display(self) -> None:
        logging.info("Initializing display...")

        pg.init()
        pg.mixer.init(size=32)

        self.pygame_info = pg.display.Info()
        self.WIDTH = self.pygame_info.current_w
        self.HEIGHT = self.pygame_info.current_h

        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.FULLSCREEN | pg.DOUBLEBUF | pg.HWSURFACE, display=0)

        self.clock = pg.time.Clock()

    def init_menu_interface(self) -> None:
        logging.info("Initializing menu interface...")

        font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 30)

        self.enter_cartridge_surf = font.render("Enter game cartridge...", True, (255, 255, 255))
        self.enter_cartridge_rect = pg.Rect(self.WIDTH // 2 - self.enter_cartridge_surf.width // 2, self.HEIGHT // 2 - self.enter_cartridge_surf.height // 2, self.enter_cartridge_surf.width, self.enter_cartridge_surf.height)
        self.enter_cartridge_vel = [random.choice([3, -3]), random.choice([3, -3])]

    def init_cartridges(self) -> None:
        logging.info("Initializing cartridges...")

        self.cartridge_loader = CartridgeLoader(self.on_title_launch)
        self.cartridge_loaded = False

    def load_cartidge(self) -> None:
        self.cartridge_loader.load_cartridge()

    def check_cartridge(self) -> None:
        if self.TESTING: return

        last_cartridge_loaded = self.cartridge_loaded

        while self.cartridge_loader.init_failure:
            logging.warning("Attempting to restart cartridge loadeder to reset SD loader (init failure)...")
            self.cartridge_loader.__init__(self.on_title_launch)

            if self.cartridge_loader.init_failure:
                logging.error("Failed to re-init cartridge loader! Waiting 1 second before retrying...")
                sleep(1)

        while 1:
            if time() - self.last_cartridge_update_check > 2:
                self.last_cartridge_update_check = time()
                cartridge_loaded = self.cartridge_loader.is_sd_card_connected()

                if cartridge_loaded is not None: self.cartridge_loaded = cartridge_loaded

            else:
                sleep(time() - self.last_cartridge_update_check)

            if not self.cartridge_loaded:
                self.on_cartridge_remove()
                self.init_cartridges()
                self.check_cartridge()
                return

            elif not last_cartridge_loaded:
                self.cartridge_loaded = True

            if self.cartridge_loaded: return

    def on_cartridge_remove(self) -> None:
        logging.warning(f"Cartridge no longer reading / writing (disconnected)!")

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

        self.load_cartidge()
        self.main() # Reset when the game stops (cartridge unloaded)

    def update(self) -> bool:
        """Returns: should_quit"""

        self.controller_manager.update()
        
        if self.cartridge_loaded == False: return True

        return False

    def on_title_launch(self, ConsoleEntry: object) -> None:
        while not self.init:
            sleep(0.1)

        self.cartridge_loaded = True

        ConsoleEntry(self.screen, self.update, self.controller_manager.get_num_players, self.controller_manager.controllers)

        self.main()

if __name__ == "__main__":
    # Where it all begins...
    testing = True

    if len(argv) > 1:
        if argv[1] == "--test":
            testing = True
        else:
            raise Exception(f"Argument {argv[1]} is not recognised! Use --test for console testing.")

    console = Console(testing)