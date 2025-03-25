import logging

try:
    from gpiozero import Device
    from gpiozero.pins.pigpio import PiGPIOFactory

    Device.pin_factory = PiGPIOFactory()

    from gpiozero import MCP3008
except:
    def MCP3008(**args) -> None: ...
    logging.error("Failed to import gpiozero library for controller interfaceing! Assuming this is a non-console test so continuing...")

def ErrMCP3008(**args) -> None: ...

from Controllers.controller import Controller

class ControllerManager:
    NUM_CONTROLLER_PORTS = 4

    CONTROLLER_STATUS_PINS = {
        0: 5,
        1: 6,
        2: 13,
        3: 19
    }

    def __init__(self, testing: bool = False) -> None:
        self.TESTING = testing

        try:
            self.controllers = [
                Controller(i, MCP3008(channel=i*2, select_pin=8), MCP3008(channel=i*2+1, select_pin=8), self.CONTROLLER_STATUS_PINS[i], testing=self.TESTING)
                for i in range(self.NUM_CONTROLLER_PORTS)
            ]

        except Exception as e:
            logging.error(f"MCP3008 (Controller Managemnet Device) - Not Found! Error: {e}. No controllers working...")

            self.controllers = [
                Controller(i, ErrMCP3008(channel=i*2, select_pin=8), ErrMCP3008(channel=i*2+1, select_pin=8), self.CONTROLLER_STATUS_PINS[i], testing=self.TESTING)
                for i in range(self.NUM_CONTROLLER_PORTS)
            ]

    def get_num_players(self) -> int:
        num_players = 0

        for controller in self.controllers:
            if controller.plugged_in: num_players += 1

        return num_players

    def update(self) -> None:
        for controller in self.controllers:
            controller.poll_events()