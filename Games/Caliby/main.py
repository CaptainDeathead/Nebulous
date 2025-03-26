import pygame as pg

from Console.Controllers.controller import Controller, CONTROLS

from typing import List

class VController:
    def __init__(self, controller: Controller, width: int, height: int) -> None:
        self.controller = controller
        self.width = width
        self.height = height

        self.surface = pg.Surface((self.width, self.height), pg.SRCALPHA)

        self.button_positions = {
            CONTROLS.DPAD.UP: (150, 100),
            CONTROLS.DPAD.LEFT: (100, 150),
            CONTROLS.DPAD.DOWN: (150, 200),
            CONTROLS.DPAD.RIGHT: (200, 150),
            CONTROLS.SELECT: (250, 100),

            CONTROLS.START: (300, 100),
            CONTROLS.ABXY.X: (350, 150),
            CONTROLS.ABXY.A: (400, 200),
            CONTROLS.ABXY.B: (450, 150),
            CONTROLS.ABXY.Y: (400, 100)
        }

    def draw(self) -> pg.Surface:
        pg.draw.rect(self.surface, (100, 100, 100), (0, 0, self.width, self.height), border_radius=10)
        pg.draw.rect(self.surface, (255, 255, 255), (50, 50, self.width - 100, self.height - 100), border_radius=10)

        pressed_button_types = []
        for event in self.controller.event.get():
            pressed_button_types.append(event.type)

        for button, button_pos in self.button_positions.items():
            if button in pressed_button_types:
                pg.draw.circle(self.surface, (255, 0, 0), button_pos, radius=20)
            else:
                pg.draw.circle(self.surface, (0, 0, 255), button_pos, radius=20)

        return self.surface

class Caliby:
    VCONTROLLER_WIDTH = 550
    VCONTROLLER_HEIGHT = 300
    VCONTROLLER_PADDING = 100

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers

        self.clock = pg.time.Clock()

        self.vcontrollers = [VController(self.controllers[i], width=self.VCONTROLLER_WIDTH, height=self.VCONTROLLER_HEIGHT) for i in range(4)]

        self.main()

    def main(self) -> None:
        while 1:
            dt = self.clock.tick(60)
            self.display_surf.fill((0, 0, 0))

            for event in pg.event.get():
                ...
            
            curr_x = 0
            curr_y = 200
            for i, vcontroller in enumerate(self.vcontrollers):
                self.display_surf.blit(vcontroller.draw(), (curr_x + self.VCONTROLLER_PADDING, curr_y))

                curr_x += self.VCONTROLLER_PADDING + self.VCONTROLLER_WIDTH

                if curr_x >= (self.VCONTROLLER_PADDING + self.VCONTROLLER_WIDTH) * 2:
                    curr_x = 0
                    curr_y = 600

            self.console_update()

            pg.display.flip()