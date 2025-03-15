#code "borrowed" from /Games/Snither/main.py
#remember to probably add multiple lives
import pygame as pg

from Console.UI.pygame_gui import Button
from Console.Controllers.controller import Controller, CONTROLS

from time import time
from random import randint

from typing import Sequence, List, Tuple, Dict

pg.init()

FONTS_PATH = "./UI/Fonts"

class DIRECTION:
    UP    = 1
    RIGHT = 4
    DOWN  = 2
    LEFT  = 3

    @property
    def RANDOM(self) -> int: return randint(1, 4)

class Bullet:
    def __init__(self, location: Tuple[int, int], color: pg.Color, direction: int):
        self.x = location[0]
        self.y = location[1]
        self.color = color
        self.speed = 10
        self.direction = direction

        if direction > 2:
            self.height = 4
            self.width = 8
        else:
            self.height = 8
            self.width = 4
    
    def move(self, surface: pg.Surface) -> None:
        match self.direction:
            case 1:
                self.y -= self.speed
            case 2: 
                self.y += self.speed
            case 3:
                self.x -= self.speed
            case 4:
                self.x += self.speed
        pg.draw.rect(surface, self.color, pg.Rect(self.x, self.y, self.width, self.height))

class Ship:
    PART_SIZE = 50

    def __init__(self, location: Tuple[int, int], color: pg.Color) -> None:
        self.x = location[0]
        self.y = location[1]

        self.direction = 4
        self.speed = 5
        self.scale = 10

        self.score = 0
        self.color = color
        self.dead = False

    def draw(self, surface) -> None:
        match self.direction:
            case 1:
                points = [(5*self.scale+self.x,5*self.scale+self.y), (1+self.x, 5*self.scale+self.y), (3*self.scale+self.x, 1+self.y)]
            case 2:
                points = [(5*self.scale+self.x,1+self.y), (1+self.x, 1+self.y), (3*self.scale+self.x, 5*self.scale+self.y)]
            case 3:
                points = [(5*self.scale+self.x, 1+self.y), (5*self.scale+self.x, 5*self.scale+self.y), (1+self.x, 3*self.scale+self.y)]
            case 4:
                points = [(1+self.x, 1+self.y), (1+self.x, 5*self.scale+self.y), (5*self.scale+self.x, 3*self.scale+self.y)]
            case _:
                n = 1
                while True:
                    print("LinusTechTrips"*n)
                    n += 1

        pg.draw.polygon(surface, self.color, points)

    def move_up(self) -> None: self.direction = 1; self.y -= self.speed
    def move_right(self) -> None: self.direction = 4; self.x += self.speed
    def move_down(self) -> None: self.direction = 2; self.y += self.speed
    def move_left(self) -> None: self.direction = 3; self.x -= self.speed

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
    TIMER_LENGTH = 1

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

        self.title_lbl = self.fonts["large"].render("Meteors", True, (255, 255, 255))

        self.info_lbl = self.fonts["medium"].render   ("Press A to ready / unready...", True, (255, 255, 255))
        self.info_lbl.blit(self.fonts["medium"].render("      A", True, (0, 255, 0)))


        self.timer_active = False
        self.timer_time = self.TIMER_LENGTH
        self.timer_start_time = time()
        self.start_game = False

        self.timer_start_lbl = self.fonts["medium"].render("Game starting in  ...", True, (255, 255, 255))
        self.timer_end_lbls = [self.fonts["medium"].render(f"                 {i}", True, (0, 0, 255)) for i in range(self.timer_time, -1, -1)]

        self.players[0].ready = True
        self.players[0].controller.plugged_in = True

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
        self.timer_time = self.TIMER_LENGTH
        self.timer_last_update = time()

    def check_game_start(self) -> None:
        for player in self.players:
            if player.controller.plugged_in and not player.ready:
                self.reset_timer()
                return
            
            self.timer_time = time() - self.timer_start_time
            self.timer_active = True

            if self.timer_time >= self.TIMER_LENGTH:
                self.start_game = True

    def main(self) -> None:
        while not self.start_game:
            self.display_surf.fill((0, 0, 0))
            self.clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pass

            for i, controller in enumerate(self.controllers):
                for event in controller.event.get():
                    if event.type == CONTROLS.ABXY.A:
                        self.players[i].ready = not self.players[i].ready

            self.draw_player_buttons()

            self.display_surf.blit(self.title_lbl, (self.width // 2 - self.title_lbl.width // 2, 100))
            
            if self.timer_active:
                curr_time_int = max(0, min(int(round(self.timer_time, 0)), len(self.timer_end_lbls) - 1))
                self.display_surf.blit(self.timer_start_lbl, (self.width // 2 - self.timer_start_lbl.width // 2, self.height - 200))
                self.display_surf.blit(self.timer_end_lbls[curr_time_int-1], (self.width // 2 - self.timer_start_lbl.width // 2, self.height - 200))
            else:
                self.display_surf.blit(self.info_lbl, (self.width // 2 - self.info_lbl.width // 2, self.height - 200))

            self.check_game_start()

            self.console_update()

            pg.display.flip()

class Meteors:
    PYGAME_INFO: any = pg.display.Info()
    WIDTH: int = PYGAME_INFO.current_w
    HEIGHT: int = PYGAME_INFO.current_h
    NUM_SHIPS = 1
    PLAYING_FIELD_SIZE = -1
    STEP_INTERVAL = 0.15

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers
        self.get_num_players = get_num_players
        self.num_screens =  self.get_num_players()

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

        for i, ship in enumerate(sorted(self.ships, key=lambda ship: ship.score, reverse=True)):
            score_lbl = self.main_menu.fonts["medium"].render(f"Player {i + 1} - {ship.score}", True, ship.color)
            self.display_surf.blit(score_lbl, (self.WIDTH // 2 - 200, curr_y))

            curr_y += spacing

        cont_lbl = self.main_menu.fonts["large"].render("Press A to continue...", True, (255, 255, 255))
        cont_lbl.blit(self.main_menu.fonts["large"].render("      A", True, (0, 255, 0)))

        acc_dt = 0

        start_time = time()

        def reset_game() -> None:
            # > what
            #if time() - start_time < 5: return
            self.__init__(self.display_surf, self.console_update, self.get_num_players, self.controllers)

        while 1:
            self.clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        reset_game()
                        return
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
                    if event.key == pg.K_a:
                        #shoot bullet
                        self.bullets.append(Bullet([self.ships[0].x, self.ships[0].y], self.ships[0].color, self.ships[0].direction))
                    elif event.key == pg.K_y:
                        self.ships[0].dead = True
            
            keys = pg.key.get_pressed()  # Get the state of all keys
            if keys[pg.K_UP]:
                self.ships[0].move_up()
            elif keys[pg.K_RIGHT]:
                self.ships[0].move_right()
            elif keys[pg.K_DOWN]:
                self.ships[0].move_down()
            elif keys[pg.K_LEFT]:
                self.ships[0].move_left()

            for ship in self.ships:
                ship.draw(self.display_surf)
            for bullet in self.bullets:
                bullet.move(self.display_surf)

            if time() - self.last_snake_move_time > self.STEP_INTERVAL:
                self.last_snake_move_time = time()

                for screen in self.screens:
                    screen.fill((0, 0, 0))
                    #something goes here

                alive_player_count = 0
                alive_snake_count = 0
                alive_snake_index = 0
                for i, ship in enumerate(self.ships):
                    if not ship.dead:
                        alive_snake_index += 1
                        alive_snake_count += 1
                        alive_player_count += 1
                    
                if alive_player_count == 0:
                    self.show_game_over(alive_snake_index)
                    return

                for screen in self.screens:
                    self.display_surf.blit(screen, screen.pos)

            self.console_update()

            pg.display.flip()