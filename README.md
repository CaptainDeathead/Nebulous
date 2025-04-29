# Nebulous

Nebulous is a retro console system powered by a Raspberry Pi. Designed for both nostalgia and innovation, it offers a unique blend of custom hardware and software to deliver an exciting multiplayer gaming experience.

## Features

- **Custom Controllers**: Nebulous supports up to 4 controllers for multiplayer gaming.
- **SD Card Cartridges**: Games are loaded via SD card cartridges, offering a retro game-swapping experience.
- **3D Printed Shell**: The physical console is encased in a sleek and durable 3D-printed shell.
- **Custom Games**: Includes a variety of games designed specifically for Nebulous (see the list below).
- **NES Game Support**: Play classic `.nes` files for old NES games.

## Custom Games

The `games` directory contains the following games created specifically for Nebulous using Pygame:

- **Caliby**: A calibration tool for testing controllers with the Nebulous.
- **Meteors**: A 4-player Asteroids clone.
- **Pong**: The classic Pong game.
- **Shape Royale**: A class-based battle royale where you play as 2D shapes.
- **Snither**: A multiplayer merge of Slither.io and classic Snake.
- **Tetris**: A 4-player version of the timeless Tetris game.

## Design Files

All files related to the physical design of Nebulous are located in the `/design` directory, including:

- **3D Printing Files**: Models for the Nebulous shell.
- **Controller PCB Designs**: Schematics and layouts for custom controllers.
- **Wiring Designs**: Diagrams and plans for wiring the console, controllers, and other components.

## How It Works

- **Without Cartridge**: If no game cartridge is inserted, the console will prompt you to insert one.
- **With Cartridge**: When a cartridge is inserted, the console attempts to load and play the game.

## Getting Started

1. **Hardware Setup**:
   - Assemble the 3D-printed case using files from the `/design` directory.
   - Connect up to 4 custom controllers using the provided PCB and wiring designs.
   - Insert an SD card cartridge containing your desired game.

2. **Software Setup**:
   - Clone the repository:
     ```bash
     git clone https://github.com/CaptainDeathead/Nebulous.git
     ```
   - Navigate to the `rpi-install` directory and run the `install.sh` script to set up the console:
     ```bash
     cd Nebulous/rpi-install
     ./install.sh
     ```

3. **Running Games**:
   - Insert a game cartridge to start playing.
   - Alternatively, load a `.nes` file for older NES games.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for bug reports and feature suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
