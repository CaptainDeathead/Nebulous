from Controllers.controller import Controller

class ControllerManager:
    NUM_CONTROLLER_PORTS = 4

    def __init__(self) -> None:
        self.controllers = [Controller(i) for i in range(self.NUM_CONTROLLER_PORTS)]

    def get_num_players(self) -> int:
        num_players = 0

        for controller in self.controllers:
            if controller.plugged_in: num_players += 1

        return num_players

    def update(self) -> None:
        for controller in self.controllers:
            controller.check_plugged_status()

            if controller.plugged_in:
                controller.poll_events()