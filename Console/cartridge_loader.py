import os
import sys
import tarfile
import logging
import importlib

try:
    from spidev import SpiDev
except:
    TESTING = True
    SpiDev = None
    logging.warning("No spidev module detected! Assuming this is a test!")

from shutil import rmtree
from io import BytesIO
from zipfile import ZipFile
from time import sleep

class CartridgeLoader:
    SD_BLOCK_SIZE = 512

    def __init__(self, on_title_launch: object) -> None:
        self.on_title_launch = on_title_launch

        try:
            self.spi = SpiDev()
            self.spi.open(0, 1) # SPI Bus 0 CE1 (GPIO 7)
            self.spi.max_speed_hz = 4_000_000 # 4 MHz
        except Exception as e:
            logging.error(f"Failed to initialize cartridge (sd) SPI interface!!! Error: {e}! Assuming this is a non-console test so continuing...")

    def send_command(self, cmd: int, arg: int) -> bytes:
        # Send SPI command to the SD card
        # This is absolute majic that is definitly not worth the time to learn
        cmd_packet = [0x40 | cmd] + [(arg >> (8 * i)) & 0xFF for i in range(3, -1, -1)] + [0x95]
        self.xfer2(cmd_packet)
        sleep(0.1) # Allow time for a response

        return self.spi.xfer2([0xFF]) # Get response

    def sd_init(self) -> bool:
        # Init SD card in SPI mode
        for _ in range(10):
            # Send 80 clock pulses to enter SPI mode
            # SD card requires at least 74 clock pulses
            self.spi.xfer2([0xFF])

        # CMD0: Go idle
        # This command resets the SD card ready for use
        response = self.send_command(0, 0)

        # 0x01 Means it is in it's idle state
        if response[0] != 0x01:
            raise Exception("Error while reading cartridge! SD Card init failed!!!")

        return True

    def read_sector(self, sector: int) -> bytes:
        self.send_command(17, sector) # CMD17: Read single block

        while 1:
            # Just waiting for 0xFE to be recieved
            # I think that means it's ready to send data
            response = self.spi.xfer2([0xFF])[0]

            if response == 0xFE: # Data token
                break

        data = self.spi.xfer2([0xFF] * self.SD_BLOCK_SIZE) # Reads the block with the given block size
        self.spi.xfer2([0xFF] * 2) # Ignore CRC (last 2 bytes)

        return bytes(data)

    def unzip_inmemory(self, zip_data: bytes) -> str:
        # Converts the zip_data into a "fake" file (filelike object)
        zip_buffer = BytesIO(zip_data)

        # Opens the zip from memory
        with ZipFile(zip_buffer, "r") as file_bundle:
            print(f"Files in zip: {file_bundle.namelist()}")

            extracted_files = {name: file_bundle.read(name) for name in file_bundle.namelist()}

        return extracted_files

    def load_cartridge(self) -> None:
        if TESTING:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from Games.Snither.consolemain import ConsoleEntry
            self.on_title_launch(ConsoleEntry)
            return

        if self.sd_init():
            zip_data = b""

            game_name = self.read_sector(0).decode()

            logging.info(f"Loading {game_name} from cartridge...")

            for i in range(1, 100): # Read first 100 sectors (50KB)
                zip_data += self.read_sector(i)

            tmp_game_path = f"/tmp/Games/{game_name}/"

            if os.path.exists('/tmp/Games'):
                logging.debug("Cartridge already has an entry in /tmp! Removing it...")
                rmtree('/tmp/Games', ignore_errors=True)

            os.mkdir('/tmp/Games')

            xz_buffer = BytesIO(zip_data)

            logging.debug("Extracting .tar.xz file into new /tmp directory...")
            with tarfile.open(xz_buffer, 'r:xz') as tar:
                tar.extractall(path=tmp_game_path)

            sys.path.append('/tmp') # Makes all the files in there discoverable.
            
            logging.info("Invoking ConsoleEntry from consolemain in the unzipped game...")
            try:
                consolemain = importlib.import_module(f"Games.{game_name}.consolemain")
                self.on_title_launch(consolemain.ConsoleEntry)
            except:
                raise Exception("Failed to import ConsoleEntry from consolemain!")
        else:
            raise Exception("sd_init Failed! Something unclear went wrong when initializing the SD card. Check above logs for more possible info.")