#code "borrowed" from /Games/Snither/main.py
#remember to probably add multiple lives
import pygame as pg

from Console.UI.pygame_gui import Button
from Console.Controllers.controller import Controller, CONTROLS

from time import time
from random import randint

from typing import Sequence, List, Tuple, Dict

pg.init()

FONTS_PATH = "./Console/UI/Fonts"

class DIRECTION:
    UP    = 1
    RIGHT = 2
    DOWN  = 3
    LEFT  = 4
    NEIN = 31415

    @property
    def RANDOM(self) -> int: return randint(0, 3)

class Bullet:
    def __init__(self, location: Tuple[int, int], color: pg.Color, direction: int):
        self.x = location[0]
        self.y = location[1]
        self.color = color
        self.direction = direction

        if direction % 2 == 0:
            self.height = 4
            self.width = 8
        else:
            self.height = 8
            self.width = 4
    
    def move(self, surface: pg.Surface) -> None:
        self.x += 1
        self.y += 1
        pg.draw.rect(surface, self.color, pg.Rect(self.x, self.y, self.width, self.height))

class Ship:
    PART_SIZE = 50

    def __init__(self, location: Tuple[int, int], color: pg.Color) -> None:
        self.x = location[0]
        self.y = location[1]
        self.direction = DIRECTION.RANDOM

        self.score = 0
        self.color = color
        self.dead = False

    def draw(self, surface) -> None:
        match self.direction:
            case DIRECTION.UP:
                points = [(1+self.x, 1+self.y), (1+self.x, 5+self.y), (5+self.x, 3+self.y)]
            case DIRECTION.DOWN:
                points = [(5+self.x, 1+self.y), (5+self.x, 5+self.y), (1+self.x, 3+self.y)]
            case DIRECTION.LEFT:
                points = [(5+self.x,5+self.y), (1+self.x, 5+self.y), (3+self.x, 1+self.y)]
            case DIRECTION.RIGHT:
                points = [(5+self.x,1+self.y), (1+self.x, 1+self.y), (3+self.x, 5+self.y)]
            case _:
                n = 1
                while True:
                    print("LinusTechTrips"*n)
                    n += 1

        pg.draw.polygon(surface, self.color, points)

    def move_up(self, speed: int | float) -> None: self.direction = DIRECTION.UP; self.y += speed
    def move_right(self, speed: int | float) -> None: self.direction = DIRECTION.RIGHT; self.x += speed
    def move_down(self, speed: int | float) -> None: self.direction = DIRECTION.DOWN; self.y -= speed
    def move_left(self, speed: int | float) -> None: self.direction = DIRECTION.LEFT; self.x -= speed

class Screen(pg.Surface):
    def __init__(self, rect: pg.Rect, flags: int = 0) -> None:
        self.positioning_rect = rect

        super().__init__(rect.size, flags)

    @property
    def x(self) -> int: return self.positioning_rect.x

    @property
    def y(self) -> int: return self.positioning_rect.y

    @property
    def pos(self) -> Sequence[int]: return (self.positioning_rect.x, self.positioning_rect.y)

class Player:
    def __init__(self) -> None:
        ...

class MainMenu:
    def __init__(self, display_surf: pg.Surface) -> None:
        self.display_surf = display_surf

        self.width = display_surf.width
        self.height = display_surf.height

        self.fonts = {
            "small": pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 20),
            "medium": pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 30),
            "large": pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 40)
        }

        title_lbl = self.fonts["large"].render("Meteors", True, (255, 255, 255))
        self.display_surf.blit(title_lbl, (self.width // 2, 20))

    def draw_player_buttons(self) -> None:
        players_box_w = 400
        players_box = pg.Rect(self.width // 2 - players_box_w // 2, self.height // 2 - players_box_w // 2, players_box_w, players_box_w)
        pg.draw.rect(self.display_surf, (150, 150, 150), players_box)

        btn_width = 300
        btn_height = 100
        btn_padding = 20

        btn_x = self.width // 2 - btn_width // 2

        curr_y = btn_padding
        for player_index in range(4):
            btn_rect = pg.Rect(btn_x, curr_y, btn_width, btn_height)
            pg.draw.rect(self.display_surf, (200, 200, 200), btn_rect)

            player_ready_text_start = self.fonts["small"].render(f"Player {player_index + 1} - ", True, (255, 255, 255))
            player_ready_text_end = self.fonts["small"].render(f"{self.players[player_index].ready_text}", True, self.players[player_index].ready_color)

            self.display_surf.blit(player_ready_text_start, (self.width // 2 - (player_ready_text_start.width + player_ready_text_end.width) // 2, curr_y))
            self.display_surf.blit(player_ready_text_end, (self.width // 2 - (player_ready_text_start.width + player_ready_text_end.width) // 2 + player_ready_text_start.width, curr_y))

            curr_y += btn_height + btn_padding

class Meteors:
    PYGAME_INFO: any = pg.display.Info()
    WIDTH: int = PYGAME_INFO.current_w
    HEIGHT: int = PYGAME_INFO.current_h
    NUM_SHIPS = 4
    PLAYING_FIELD_SIZE = -1
    STEP_INTERVAL = 0.15

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers

        self.main_menu = MainMenu(self.display_surf, self.console_update, self.controllers)

        self.screens = [Screen(pg.Rect(0, 0, self.WIDTH, self.HEIGHT), pg.SRCALPHA)]
        self.clock = pg.time.Clock()

        self.ships = [Ship((randint(0, 69), randint(0, 69)), (255, 0, 0)) for _ in range(self.NUM_SHIPS)]
        self.bullets = []
        self.last_snake_move_time = time()

        self.display_surf.fill((0, 0, 0))

        self.main()

    def show_game_over(self, alive_snake_index: int | None) -> None:
        self.display_surf.fill((0, 0, 0, 128))

        go_lbl = self.main_menu.fonts["large"].render("Game Over!", True, (255, 255, 255))
        self.display_surf.blit(go_lbl, (self.WIDTH // 2 - go_lbl.width // 2, 100))

        winner_lbl = self.main_menu.fonts["medium"].render(f"Player {alive_snake_index + 1} survived the longest!", True, (255, 255, 255))
        winner_lbl.blit(self.main_menu.fonts["medium"].render(f" " * len(f"Player {alive_snake_index + 1} survived the ") + "longest", True, (255, 150, 0)), (0, 0))

        self.display_surf.blit(winner_lbl, (self.WIDTH // 2 - winner_lbl.width // 2, 100 + go_lbl.height + 50))

        scores_lbl = self.main_menu.fonts["large"].render("Scores:", True, (255, 255, 255))
        scores_lbl_y = 100 + go_lbl.height + 50 + winner_lbl.height + 50
        self.display_surf.blit(scores_lbl, (self.WIDTH // 2 - scores_lbl.width // 2, scores_lbl_y))

        curr_y = scores_lbl_y + scores_lbl.height + 20 + 30
        spacing = 40

        for i, ship in enumerate(sorted(self.ships, key=lambda ship: len(ship.score), reverse=True)):
            score_lbl = self.main_menu.fonts["medium"].render(f"Player {i + 1} - {len(ship.score)}", True, ship.og_color)
            self.display_surf.blit(score_lbl, (self.WIDTH // 2 - 200, curr_y))

            curr_y += spacing

        cont_lbl = self.main_menu.fonts["large"].render("Press A to continue...", True, (255, 255, 255))
        cont_lbl.blit(self.main_menu.fonts["large"].render("      A", True, (0, 255, 0)))

        acc_dt = 0

        while 1:
            acc_dt += self.clock.tick(60)

            for event in pg.event.get():
                pass

            if acc_dt >= 5:
                self.display_surf.blit(cont_lbl, (self.WIDTH // 2 - cont_lbl.width // 2, curr_y + 40))

                for controller in self.controllers:
                    for event in controller.event.get():
                        if event.type == CONTROLS.ABXY.A:
                            self.__init__(self.display_surf, self.console_update, self.get_num_players, self.controllers)
                            return

            self.console_update()

            pg.display.flip()

    def main(self) -> None:
        while 1:
            self.clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pass
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.snakes[0].face_up()
                    elif event.key == pg.K_RIGHT:
                        self.snakes[0].face_right()
                    elif event.key == pg.K_DOWN:
                        self.snakes[0].face_down()
                    elif event.key == pg.K_LEFT:
                        self.snakes[0].face_left()
                    elif event.key == pg.K_a:
                        #shoot bullet
                        self.bullets.append(Bullet([self.ships[0].x, self.ships[1].y], self.ships[0].color), self.ships[0].direction)
                        

            if time() - self.last_snake_move_time > self.STEP_INTERVAL:
                self.last_snake_move_time = time()

                for screen in self.screens:
                    screen.fill((0, 0, 0))
                    #something goes here

                alive_player_count = 0
                alive_snake_index = None
                for i, ship in enumerate(self.ships):
                    if not ship.dead:
                        alive_snake_index = i
                    ship.move()
                    
                if alive_player_count == 0:
                    self.show_game_over(alive_snake_index)
                    return

                for screen in self.screens:
                    self.display_surf.blit(screen, screen.pos)

            self.console_update()

            pg.display.flip()