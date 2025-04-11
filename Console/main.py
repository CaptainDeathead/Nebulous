import pygame as pg
import random
import logging
import os

from Controllers.controller import Controller
from Controllers.controller_manager import ControllerManager
from cartridge_loader import CartridgeLoader
from console_io import IOManager
from time import sleep, time
from threading import Thread
from sys import argv
from traceback import format_exc

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

FONTS_PATH = "./UI/Fonts"

class Console:
    """
    FIRMWARE FOR NEBULOUS CONSOLE
    """

    CONSOLE_NAME = "Nebulous REV. A - PROTO"
    TARGET_FIRMWARE_INFO = {
        "CONSOLE_NAME": CONSOLE_NAME,
        "HOST_TYPE": "Linux - Raspberry Pi OS DESKTOP",
        "FIRMWARE_VERSION": "1.1.0",
        "REQUIREMENTS": ["Restart console to load new cartridge (auto detection causing controller lag)"]
    }

    # Allows the console to write data to the cartridge, and verify it is the same to check if cartridge is still inserterd
    # WARNING: THIS CAN CAUSE INTERUPTIONS TO THE CONTROLLER INPUTS (DELAY + GHOSTING)
    # WARNING: THIS CAN HAVE INCONSISTENT BEHAVIOUR WHEN PAIRED WITH CONTROLLERS (RANDOM FAILED READS / WRITES)
    CARTRIDGE_READ_CHECK = False
    USE_CONTROLLER_THREAD = False

    NUM_CONTROLLER_PORTS = 4
    TARGET_FPS = 60 # Only affects menu
    TESTING = False # Allows testing in a non-console environment

    def __init__(self, testing: bool = False, flashing: bool = False) -> None:
        """
        Steps to initialize console:
        1. Initialize console input / output devices (io)
        2. Initialize controllers and controller polling
        3. Initialize display and screen
        4. Load into blank console interface
        5. Initialize cartridge loading
        """

        self.init = False
        self.TESTING = testing
        self.FLASHING = flashing

        logging.info("Welcome from the console!!!\n")

        for key, value in self.TARGET_FIRMWARE_INFO.items():
            logging.info(f"{key}: {value}")

        print()

        self.init_io()
        self.init_controllers()
        self.init_display()
        self.init_menu_interface()
        self.init_cartridges()

        # All threads will read this every time they update and safely shutdown if it is True.
        # Used to shutdown console safely.
        self.kill_threads = False

        self.update_controllers = False # Allows for cartridge reader to "read check" its status 'safely'.
        self.controller_check_thread = Thread(target=self.check_controllers)
        if self.USE_CONTROLLER_THREAD:
            self.controller_check_thread.start()

        self.last_cartridge_update_check = 0
        self.cartridge_check_thread = Thread(target=self.check_cartridge)
        self.cartridge_check_thread.start()

        self.init = True
        logging.info("Console startup complete!")

        if self.TESTING: self.load_cartidge()

        self.main()

    def final_console_shutdown(self) -> None:
        logging.info("Recieved shutdown signal! Don't leave me!!!")

        logging.debug("Waiting for threads to shutdown...")
        self.kill_threads = True
        self.cartridge_check_thread.join()
        if self.USE_CONTROLLER_THREAD:
            self.controller_check_thread.join()

        self.cartridge_loader.unload_cartridge()

        logging.info("Executing 'Nebulous:/Console$ sudo shutdown now'...")
        os.system("sudo shutdown now") # WARNING: Requires 'sudo' to not have a password
        exit(0)

    def init_io(self) -> None:
        logging.info("Initializing console io manager...")

        self.io_manager = IOManager(self.TESTING, self.final_console_shutdown)

    def init_controllers(self) -> None:
        logging.info("Initializing controllers...")

        self.controller_manager = ControllerManager(testing=self.TESTING)

    def init_display(self) -> None:
        logging.info("Initializing display...")

        pg.init()

        try:
            pg.mixer.init(size=32)
        except:
            logging.error("Failed to initialize audio!")
            logging.error(format_exc())


        self.pygame_info = pg.display.Info()
        self.WIDTH = self.pygame_info.current_w
        self.HEIGHT = self.pygame_info.current_h

        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.FULLSCREEN | pg.DOUBLEBUF | pg.HWSURFACE, display=0)

        self.clock = pg.time.Clock()

        pg.mouse.set_visible(False)

    def init_menu_interface(self) -> None:
        logging.info("Initializing menu interface...")

        font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 30)

        self.enter_cartridge_surf = font.render("Enter game cartridge...", True, (255, 255, 255))
        self.enter_cartridge_rect = pg.Rect(self.WIDTH // 2 - self.enter_cartridge_surf.width // 2, self.HEIGHT // 2 - self.enter_cartridge_surf.height // 2, self.enter_cartridge_surf.width, self.enter_cartridge_surf.height)
        self.enter_cartridge_vel = [random.choice([3, -3]), random.choice([3, -3])]

    def init_cartridges(self) -> None:
        logging.info("Initializing cartridges...")

        self.cartridge_loader = CartridgeLoader(self.on_title_launch, self.FLASHING)
        self.cartridge_loaded = False

    def load_cartidge(self) -> None:
        self.cartridge_loader.load_cartridge()

    def check_controllers(self) -> None:
        while not self.kill_threads:
            if not self.update_controllers:
                sleep(0.01)
                continue

            self.controller_manager.update()
            sleep(0.01)

    def check_cartridge(self) -> None:
        if self.TESTING: return

        last_cartridge_loaded = self.cartridge_loaded

        while self.cartridge_loader.init_failure:
            if self.kill_threads: return

            self.update_controllers = False

            logging.warning("Attempting to restart cartridge loadeder to reset SD loader (init failure)...")
            self.cartridge_loader.__init__(self.on_title_launch)

            if self.cartridge_loader.init_failure:
                logging.error("Failed to re-init cartridge loader! Waiting 1 second before retrying...")
                sleep(1)

        while not self.kill_threads:
            if self.CARTRIDGE_READ_CHECK:
                if time() - self.last_cartridge_update_check > 2:
                    self.last_cartridge_update_check = time()

                    self.update_controllers = False
                    cartridge_loaded = self.cartridge_loader.is_sd_card_connected()
                    self.update_controllers = True

                    if cartridge_loaded is not None: self.cartridge_loaded = cartridge_loaded

                else:
                    sleep(time() - self.last_cartridge_update_check)

            if not self.cartridge_loaded and self.CARTRIDGE_READ_CHECK:
                self.on_cartridge_remove()
                self.init_cartridges()
                self.check_cartridge()
                return

            elif not last_cartridge_loaded:
                self.cartridge_loaded = True

                if not self.CARTRIDGE_READ_CHECK:
                    logging.warning("Cartridge read checking disabled! Killing cartridge check thread...")
                    return

            #if self.cartridge_loaded: return

    def on_cartridge_remove(self) -> None:
        logging.warning(f"Cartridge no longer reading / writing (disconnected)!")

    def on_game_crash(self) -> None:
        self.screen.fill((255, 0, 0))
        
        title_font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 50)
        self.screen.blit(title_font.render("GAME CRASH!", True, (255, 255, 255)), (100, 100))

        instructions_font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 30)
        self.screen.blit(instructions_font.render("Restart the console using the front IO switch to safely recover.", True, (0, 255, 255), wraplength=self.WIDTH - 100), (100, 200))

        error_font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 20)
        self.screen.blit(error_font.render(f"Error:\n{format_exc()}", True, (0, 0, 0), wraplength=self.WIDTH - 200), (100, 300))

        pg.display.flip()
        
        while 1:
            self.clock.tick(self.TARGET_FPS)

            for event in pg.event.get():
                ...

            self.update()

    def main(self) -> None:
        while not self.cartridge_loaded:
            self.delta_time = self.clock.tick(self.TARGET_FPS)
            self.screen.fill((0, 0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pass

            self.update()

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

        self.io_manager.set_led_on()
        self.io_manager.update()
        self.controller_manager.update()
        
        if self.cartridge_loaded == False: return True

        return False

    def on_title_launch(self, ConsoleEntry: object) -> None:
        while not self.init:
            sleep(0.1)

        self.cartridge_loaded = True
        self.update_controllers = True

        try:
            ConsoleEntry(self.screen, self.update, self.controller_manager.get_num_players, self.controller_manager.controllers)
        except Exception as e:
            logging.error(f"Game crashed with error: {e}!")

            logging.error(format_exc())
            
            # If the user cannot recover by unplugging cartridge then show crash screen
            if not self.CARTRIDGE_READ_CHECK:
                self.on_game_crash()
            else:
                self.main()

if __name__ == "__main__":
    # Where it all begins...
    testing = False # DO NOT CHANGE THIS VALUE!!!!! USE --test WHEN RUNNING THE SCRIPT FOR TESTING
    flashing = False

    if len(argv) > 1:
        if argv[1] == "--test":
            testing = True
        elif argv[1] == "--flash":
            flashing = True
        else:
            raise Exception(f"Argument {argv[1]} is not recognised! Use --test for console testing. Use --flash for cartridge flashing.")

    console = Console(testing, flashing)
