

class Controller:
    def __init__(self, port: int) -> None:
        self.port = port 
        self.plugged_in = False

    def poll_events(self) -> None:
        ...

    def check_plugged_status(self) -> None:
        ...