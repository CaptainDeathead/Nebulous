import logging

try:
    from gpiozero import MCP3008
    TESTING = False
except:
    def MCP3008(**args) -> None: ...
    TESTING = True
    logging.error("Failed to import gpiozero library for controller interfaceing! Assuming this is a non-console test so continuing...")

from typing import List, Generator

class DPAD_CONTROLS:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class ABXY_CONTROLS:
    A = 6
    B = 7
    X = 8
    Y = 9

class CONTROLS:
    DPAD = DPAD_CONTROLS
    SELECT = 4
    START = 5
    ABXY = ABXY_CONTROLS

    @staticmethod
    def get_control_str(control: int) -> str:
        match control:
            case 0: return "DPAD UP"
            case 1: return "DPAD RIGHT"
            case 2: return "DPAD DOWN"
            case 3: return "DPAD LEFT"
            case 4: return "SELECT"
            case 5: return "START"
            case 6: return "A"
            case 7: return "B"
            case 8: return "X"
            case 9: return "Y"

class ActualEvent:
    def __init__(self, type: int) -> None:
        self.type = type

class Event:
    events = []

    def get(self) -> Generator[any, any, any]:
        # Returns the events in the contoller and clears them
        for event in self.events:
            yield event
            self.events.remove(event)

    def register(self, event: int) -> None:
        for event_class in self.events:
            if event_class.type == event: return

        logging.debug(f"Controller recieved {CONTROLS.get_control_str(event)}.")

        self.events.append(ActualEvent(event))

class Controller:
    def __init__(self, port: int, left_channel: MCP3008, right_channel: MCP3008, testing: bool = TESTING) -> None:
        self.port = port 
        self.plugged_in = False
        
        self.left_channel = left_channel
        self.right_channel = right_channel

        self.testing = testing

        self.event = Event()

    def split_channel_value(self, channel: MCP3008, value: float, tolerance: float = 0.05) -> bool:
        ch_value = channel.value

        if value > ch_value - tolerance and value < ch_value + tolerance:
            return True

        return False

    def poll_events(self) -> None:
        if self.testing: return

        d_up = self.split_channel_value(self.left_channel, 0.2)
        d_right = self.split_channel_value(self.left_channel, 0.4)
        d_down = self.split_channel_value(self.left_channel, 0.6)
        d_left = self.split_channel_value(self.left_channel, 0.8)
        select = self.split_channel_value(self.left_channel, 1.0)

        a = self.split_channel_value(self.right_channel, 0.2)
        b = self.split_channel_value(self.right_channel, 0.4)
        x = self.split_channel_value(self.right_channel, 0.6)
        y = self.split_channel_value(self.right_channel, 0.8)
        start = self.split_channel_value(self.right_channel, 1.0)

        if d_up: self.event.register(CONTROLS.DPAD.UP)
        if d_right: self.event.register(CONTROLS.DPAD.RIGHT)
        if d_down: self.event.register(CONTROLS.DPAD.DOWN)
        if d_left: self.event.register(CONTROLS.DPAD.LEFT)
        if select: self.event.register(CONTROLS.SELECT)

        if a: self.event.register(CONTROLS.ABXY.A)
        if b: self.event.register(CONTROLS.ABXY.B)
        if x: self.event.register(CONTROLS.ABXY.X)
        if y: self.event.register(CONTROLS.ABXY.Y)
        if start: self.event.register(CONTROLS.START)

    def check_plugged_status(self) -> None:
        ...