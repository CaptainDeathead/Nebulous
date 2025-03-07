
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

class ActualEvent:
    def __init__(self, type: int) -> None:
        self.type == type

class Event:
    events = []

    def get(self) -> Generator[any, any, any]:
        # Returns the events in the contoller and clears them
        for event in self.events:
            yield event
            self.events.remove(event)

class Controller:
    def __init__(self, port: int) -> None:
        self.port = port 
        self.plugged_in = False

        self.event = Event()

    def poll_events(self) -> None:
        ...

    def check_plugged_status(self) -> None:
        ...