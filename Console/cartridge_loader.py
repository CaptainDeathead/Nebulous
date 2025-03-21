import os
import sys
import tarfile
import logging
import importlib

try:
    import board
    import busio
    import digitalio
    import adafruit_sdcard
    TESTING = False
except:
    TESTING = True
    SpiDev = None
    logging.warning("No spidev module detected! Assuming this is a test!")

from shutil import rmtree
from io import BytesIO
from zipfile import ZipFile
from time import sleep

# TODO: THIS IS ONLY FOR TESTING WITHOUT SD_CARDS IN THE PI
TESTING = False

class CartridgeLoader:
    SD_BLOCK_SIZE = 512

    def __init__(self, on_title_launch: object) -> None:
        self.on_title_launch = on_title_launch

        try:
            spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            cs = digitalio.DigitalInOut(board.CE1)  # Commonly CE0 (GPIO8) or CE1 (GPIO7)
            self.sdcard = adafruit_sdcard.SDCard(spi, cs)
        except Exception as e:
            logging.error(f"Failed to initialize cartridge (sd) SPI interface!!! Error: {e}! Assuming this is a non-console test so continuing...")

    def read_sd_block(self, block_num) -> bytes:
        try:
            # Read a block (512 bytes)
            block_data = bytearray(512)
            self.sdcard.readblocks(block_num, block_data)
            return block_data
        except Exception as e:
            print("Error reading SD block:", e)

    def write_sd_block(self, block_num, data):
        try:
            # Write data to a block (ensure it's 512 bytes)
            if len(data) > 512:
                print("Data is too large for one block (max 512 bytes)")
                return
            block_data = bytearray(512)
            block_data[:len(data)] = data
            self.sdcard.writeblocks(block_num, block_data)
        except Exception as e:
            print("Error writing SD block:", e)

    def read_sd_data(self, start_block, end_block):
        data = bytearray()
        
        # Loop through each block from start_block to end_block
        for block in range(start_block, end_block + 1):
            block_data = self.read_sd_block(block)
            data.extend(block_data)
        
        return bytes(data)

    def write_sd_data(self, start_block, data):
        sector_size = 512
        data_len = len(data)
        current_block = start_block
        index = 0

        while index < data_len:
            # Calculate remaining data to write in the current sector
            remaining_space_in_sector = sector_size - (index % sector_size)
            data_to_write = data[index:index + remaining_space_in_sector]

            # Write data to the current block
            self.write_sd_block(current_block, data_to_write)
            
            # Move to the next block
            index += len(data_to_write)
            current_block += 1

        # If there's partial data left at the last block, fill the rest with blank
        if len(data) % sector_size != 0:
            remaining_blank = sector_size - (len(data) % sector_size)
            blank_data = bytes([0] * remaining_blank)
            self.write_sd_block(current_block, blank_data)

    def unzip_inmemory(self, zip_data: bytes) -> str:
        # Converts the zip_data into a "fake" file (filelike object)
        zip_buffer = BytesIO(zip_data)

        # Opens the zip from memory
        with ZipFile(zip_buffer, "r") as file_bundle:
            print(f"Files in zip: {file_bundle.namelist()}")

            extracted_files = {name: file_bundle.read(name) for name in file_bundle.namelist()}

        return extracted_files

    def flash_game(self) -> None:
        game_name = input("Enter game name with no spaces or wierd characters: ")
        game_path = input("Enter path to .tar.xz of game: ")

        with open(game_path, "rb") as f:
            xz = f.read()

        self.write_sd_data(0, game_name.encode('utf-8'))
        self.write_sd_data(1, bytes(len(xz)))
        self.write_sd_data(2, xz)

        print("Flashed")

    def load_cartridge(self) -> None:
        if TESTING:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

            from Games.Snither.consolemain import ConsoleEntry
            #from Games.Racer.consolemain import ConsoleEntry
            from Games.ShapeRoyale.consolemain import ConsoleEntry
            
            self.on_title_launch(ConsoleEntry)
            return

        self.flash_game()

        zip_data = b""

        game_name = self.read_sd_block(0).decode()
        xz_length = int.from_bytes(self.read_sd_block(1))

        logging.info(f"Loading {game_name} from cartridge...")

        zip_data = self.read_sd_data(2, xz_length-1)

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