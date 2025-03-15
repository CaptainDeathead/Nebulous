import pygame as pg

from Games.Racer.tracks.track import load_track
from Console.Controllers.controller import Controller, CONTROLS
from Console.sound import generate_sine_wave

from time import time

from typing import List

FONTS_PATH = "./UI/Fonts"

class Player:
    def __init__(self, controller: Controller) -> None:
        self.controller = controller
        self.ready = False

    @property
    def ready_text(self) -> str:
        if not self.controller.plugged_in: return "❓" # Should come out as ascii red question mark in the font
        if self.ready: return "Ready"
        else: return "Not ready"

    @property
    def ready_color(self) -> str:
        if not self.controller.plugged_in: return pg.Color(255, 0, 0)
        if self.ready: return pg.Color(0, 255, 0)
        else: return pg.Color(255, 0, 0)

class MainMenu:
    TIMER_LENGTH = 6

    def __init__(self, display_surf: pg.Surface, console_update: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.controllers = controllers

        self.clock = pg.time.Clock()

        self.players = [Player(controller) for controller in self.controllers]

        self.width = display_surf.width
        self.height = display_surf.height

        self.fonts = {
            "small": pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 16),
            "medium": pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 32),
            "large": pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 40)
        }

        self.title_lbl = self.fonts["large"].render("Racing game thing", True, (255, 255, 255))

        self.info_lbl = self.fonts["medium"].render   ("Press A to ready / unready...", True, (255, 255, 255))
        self.info_lbl.blit(self.fonts["medium"].render("      A", True, (0, 255, 0)))


        self.timer_active = False
        self.timer_start_time = time()
        self.start_game = False
        self.last_timer_time = 0
        self.timer_first_beep = True

        self.timer_start_lbl = self.fonts["medium"].render("Game starting in  ...", True, (255, 255, 255))
        self.timer_end_lbls = [self.fonts["medium"].render(f"                 {i}", True, (0, 0, 255)) for i in range(1, self.TIMER_LENGTH + 1)]

        self.players[0].ready = True
        self.players[0].controller.plugged_in = True
        #self.players[1].ready = True
        #self.players[1].controller.plugged_in = True
        #self.players[2].ready = True
        #self.players[2].controller.plugged_in = True
        #self.players[3].ready = True
        #self.players[3].controller.plugged_in = True

        self.main()

    def draw_player_buttons(self) -> None:
        self.players_box_w = 500
        self.players_box_h = 400
        players_box = pg.Rect(self.width // 2 - self.players_box_w // 2, self.height // 2 - self.players_box_w // 2, self.players_box_w, self.players_box_h)
        pg.draw.rect(self.display_surf, (150, 150, 150), players_box)

        btn_width = 400
        btn_height = 75
        btn_padding = 20

        btn_x = self.width // 2 - btn_width // 2

        curr_y = players_box.y + btn_padding
        for player_index in range(4):
            btn_rect = pg.Rect(btn_x, curr_y, btn_width, btn_height)
            pg.draw.rect(self.display_surf, (200, 200, 200), btn_rect)

            player_ready_text_start = self.fonts["small"].render(f"Player {player_index + 1} - ", True, (0, 0, 0))
            player_ready_text_end = self.fonts["small"].render(f"{self.players[player_index].ready_text}", True, self.players[player_index].ready_color)

            text_y = curr_y + btn_height // 2 - player_ready_text_start.height // 2

            self.display_surf.blit(player_ready_text_start, (self.width // 2 - (player_ready_text_start.width + player_ready_text_end.width) // 2, text_y))
            self.display_surf.blit(player_ready_text_end, (self.width // 2 - (player_ready_text_start.width + player_ready_text_end.width) // 2 + player_ready_text_start.width, text_y))

            curr_y += btn_height + btn_padding

    def reset_timer(self) -> None:
        self.timer_active = False
        self.timer_start_time = time()
        self.timer_first_beep = True

    def check_game_start(self) -> None:
        for player in self.players:
            if player.controller.plugged_in and not player.ready:
                self.reset_timer()
                return
            
            timer_time = self.TIMER_LENGTH - (time() - self.timer_start_time)
            self.timer_active = True

            if timer_time <= 1:
                self.start_game = True

    def main(self) -> None:
        while not self.start_game:
            self.display_surf.fill((0, 0, 0))
            self.clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pass
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.players[0].ready = not self.players[0].ready

            for i, controller in enumerate(self.controllers):
                for event in controller.event.get():
                    if event.type == CONTROLS.ABXY.A:
                        self.players[i].ready = not self.players[i].ready

            self.draw_player_buttons()

            self.display_surf.blit(self.title_lbl, (self.width // 2 - self.title_lbl.width // 2, 100))
            
            if self.timer_active:
                timer_time = self.TIMER_LENGTH - (time() - self.timer_start_time)

                if self.last_timer_time != int(round(timer_time, 0)):
                    if self.timer_first_beep:
                        self.timer_first_beep = False
                    else:
                        generate_sine_wave(800, 0.2, volume=0.15).play()

                    self.last_timer_time = int(round(timer_time, 0))

                curr_time_int = max(0, min(int(round(timer_time, 0)), len(self.timer_end_lbls) - 1))
                self.display_surf.blit(self.timer_start_lbl, (self.width // 2 - self.timer_start_lbl.width // 2, self.height - 200))
                self.display_surf.blit(self.timer_end_lbls[curr_time_int-1], (self.width // 2 - self.timer_start_lbl.width // 2, self.height - 200))
            else:
                self.display_surf.blit(self.info_lbl, (self.width // 2 - self.info_lbl.width // 2, self.height - 200))

            self.check_game_start()

            self.console_update()

            pg.display.flip()

class Racer:
    PYGAME_INFO: any = pg.display.Info()
    WIDTH: int = PYGAME_INFO.current_w
    HEIGHT: int = PYGAME_INFO.current_h

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers

        self.clock = pg.time.Clock()

        self.controllers = controllers

        self.main_menu = MainMenu(self.display_surf, self.console_update, self.controllers)

        import os
        print(os.getcwd())

        self.track_surface = load_track("../Games/Racer/tracks/track_4.track")

        self.main()

    def main(self) -> None:
        while 1:
            self.display_surf.fill((0, 0, 0))

            for event in pg.event.get():
                ...

            self.display_surf.blit(self.track_surface, (0, 0))

            pg.display.flip()

if __name__ == "__main__":
    Racer()