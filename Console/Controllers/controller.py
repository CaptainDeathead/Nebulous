import logging

try:
    import uinput
    from adafruit_mcp3xxx.analog_in import AnalogIn
    import RPi.GPIO as GPIO
    TESTING = False
except:
    def AnalogIn(**args) -> None: ...

    class GPIO:
        @staticmethod
        def setup(a, b, pull_up_down=0) -> None:
            return None
    
        @staticmethod
        def input(a) -> bool:
            return False

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

    @staticmethod
    def get_uinput_control_type(control: int) -> ...:
        match control:
            case 0: return uinput.BTN_DPAD_UP
            case 1: return uinput.BTN_DPAD_RIGHT
            case 2: return uinput.BTN_DPAD_DOWN
            case 3: return uinput.BTN_DPAD_LEFT
            case 4: return uinput.BTN_SELECT
            case 5: return uinput.BTN_START
            case 6: return uinput.BTN_A
            case 7: return uinput.BTN_B
            case 8: return uinput.BTN_X
            case 9: return uinput.BTN_Y

class ActualEvent:
    def __init__(self, type: int) -> None:
        self.type = type

class Event:
    def __init__(self) -> None:
        self.events = []

        self.device_event_types = [
            uinput.BTN_A,
            uinput.BTN_B,
            uinput.BTN_X,
            uinput.BTN_Y,
            uinput.BTN_DPAD_UP,
            uinput.BTN_DPAD_RIGHT,
            uinput.BTN_DPAD_DOWN,
            uinput.BTN_DPAD_LEFT,
            uinput.BTN_SELECT,
            uinput.BTN_START
        ]
        self.device = uinput.Device(self.device_event_types)

        self.events_this_frame = []

    def get(self) -> Generator[any, any, any]:
        # Returns the events in the contoller and clears them
        for event in self.events:
            yield event
            self.events.remove(event)

    def register(self, event: int) -> None:
        logging.debug(f"Controller recieved {CONTROLS.get_control_str(event)}.")

        self.events.append(ActualEvent(event))
        self.events_this_frame.append(event)

        self.device.emit(CONTROLS.get_uinput_control_type(event), 1)

    def reset_uinput(self) -> None:
        for i in range(10):
            if i not in self.events_this_frame:
                self.device.emit(CONTROLS.get_uinput_control_type(i), 0)

        self.events_this_frame = []

    def flush(self) -> None:
        self.events = []

class Controller:
    def __init__(self, port: int, left_channel: AnalogIn, right_channel: AnalogIn, status_pin: int, testing: bool = TESTING) -> None:
        self.port = port 
        
        self.left_channel = left_channel
        self.right_channel = right_channel

        self.status_pin = status_pin

        if not testing:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.status_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        else:
            logging.warning("Testing arg recieved so skipping controller pin init!")

        self.last_plugged_in = False
        self.plugged_in = False

        self.testing = testing
        #print(self.testing)

        self.event = Event()

    def on_plug(self) -> None:
        logging.info(f"Controller : {self.port} plugged in!")
        self.plugged_in = True

    def on_unplug(self) -> None:
        logging.info(f"Controller : {self.port} unplugged!")
        self.plugged_in = False

    def split_channel_value(self, ch_value: float, value: float, tolerance: float = 0.05) -> bool:
        if value > ch_value - tolerance and value < ch_value + tolerance:
            return True

        return False

    def poll_events(self) -> None:
        if self.testing: return

        #self.plugged_in = GPIO.input(self.status_pin)

        if self.plugged_in != self.last_plugged_in:
            if self.plugged_in: self.on_plug()
            else: self.on_unplug()

            self.last_plugged_in = self.plugged_in

        #if not self.plugged_in: return

        left_ch_value = self.left_channel.voltage / 3.3
        right_ch_value = self.right_channel.voltage / 3.3

        d_up = self.split_channel_value(left_ch_value, 0.2)
        d_left = self.split_channel_value(left_ch_value, 0.4)
        d_down = self.split_channel_value(left_ch_value, 0.6, tolerance = 0.04)
        d_right = self.split_channel_value(left_ch_value, 0.8, tolerance = 0.15)
        select = self.split_channel_value(left_ch_value, 1.0, tolerance = 0.04)

        y = self.split_channel_value(right_ch_value, 0.2)
        b = self.split_channel_value(right_ch_value, 0.4)
        a = self.split_channel_value(right_ch_value, 0.6, tolerance = 0.04)
        x = self.split_channel_value(right_ch_value, 0.8, tolerance = 0.15)
        start = self.split_channel_value(right_ch_value, 1.0, tolerance = 0.04)

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

        self.event.reset_uinput()