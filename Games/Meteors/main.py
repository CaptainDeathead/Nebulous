#code "borrowed" from /Games/Snither/main.py
#remember to probably add multiple lives
import pygame as pg
from Console.UI.pygame_gui import Button

from Console.Controllers.controller import Controller, CONTROLS
from Console.sound import generate_square_wave, generate_sine_wave

from time import time
from random import randint
from math import cos, sin, radians

from typing import Sequence, List, Tuple, Dict

startup_txt = """
 M     M  EEEEE  TTTTT  EEEEE  OOO   RRRR    SSS  
 MM   MM  E        T    E     O   O  R   R  S      
 M M M M  EEEE     T    EEEE  O   O  RRRR   SSS    
 M  M  M  E        T    E     O   O  R  R      S   
 M     M  EEEEE    T    EEEEE  OOO   R   R  SSS  
"""

print(startup_txt)

pg.init()

FONTS_PATH = "./UI/Fonts"

SHIP_COLOURS = {0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255), 3: (255, 255, 0)}

class DIRECTION:
    UP    = 1
    RIGHT = 4
    DOWN  = 2
    LEFT  = 3

    @property
    def RANDOM(self) -> int: return randint(1, 4)

class Bullet:
    def __init__(self, location: Tuple[int, int], color: pg.Color, direction: int, speed: int):
        self.x = location[0]
        self.y = location[1]
        self.color = color
        self.speed = speed
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

    def __init__(self, location: Tuple[int, int], color: pg.Color, speed: int) -> None:
        self.x = location[0]
        self.y = location[1]
        self.nozzle = (location[0], location[1])

        self.direction = 4
        self.speed = speed
        self.scale = 10
        
        self.tripoints = [(5*self.scale+self.x,5*self.scale+self.y), (1+self.x, 5*self.scale+self.y), (3*self.scale+self.x, 1+self.y)]

        self.score = 0
        self.color = color

        self.lives = 4
        self.dead = False
        self.apressed = False

    def draw(self, surface) -> None:
        match self.direction:
            case 1:
                self.tripoints = [(5*self.scale+self.x,5*self.scale+self.y), (1+self.x, 5*self.scale+self.y), (3*self.scale+self.x, 1+self.y)]
                if 5*self.scale+self.y < 0:
                    self.y = 1080
            case 2:
                self.tripoints = [(5*self.scale+self.x,1+self.y), (1+self.x, 1+self.y), (3*self.scale+self.x, 5*self.scale+self.y)]
                if 1+self.y > 1080:
                    self.y = 0
            case 3:
                self.tripoints = [(5*self.scale+self.x, 1+self.y), (5*self.scale+self.x, 5*self.scale+self.y), (1+self.x, 3*self.scale+self.y)]
                if 5*self.scale+self.x < 0:
                    self.x = 1920
            case 4:
                self.tripoints = [(1+self.x, 1+self.y), (1+self.x, 5*self.scale+self.y), (5*self.scale+self.x, 3*self.scale+self.y)]
                if 1+self.x > 1920:
                    self.x = 0
            case _:
                n = 1
                while True:
                    print("LinusTechTrips"*n)
                    n += 1
        if not self.dead:
            pg.draw.polygon(surface, self.color, self.tripoints)

    def move_up(self) -> None: self.direction = 1; self.y -= self.speed; self.nozzle = (3*self.scale+self.x, 1+self.y)
    def move_right(self) -> None: self.direction = 4; self.x += self.speed; self.nozzle = (5*self.scale+self.x, 3*self.scale+self.y)
    def move_down(self) -> None: self.direction = 2; self.y += self.speed; self.nozzle = (3*self.scale+self.x, 5*self.scale+self.y)
    def move_left(self) -> None: self.direction = 3; self.x -= self.speed; self.nozzle = (1+self.x, 3*self.scale+self.y)


class Rock:
    def __init__(self, radius, x, y, speed, va:float, big=True):
        self.radius = radius
        self.x = x
        self.y = y

        self.big = big
        self.speed = speed
        self.heading: float = va

        self.dx = cos(radians(self.heading)) * self.speed
        self.dy = sin(radians(self.heading)) * self.speed
    
    def move(self, surface, bound_x, bound_y):
        #self.x += self.dx
        #self.y += self.dy
        #
        #if self.x - self.radius <= 0 or self.x + self.radius >= bound_x:
        #    self.dx = -self.dx
        #    self.heading = (180 - self.heading) % 360
        #
        #if self.y - self.radius <= 0 or self.y + self.radius >= bound_y:
        #    self.dy = -self.dy
        #    self.heading = (360 - self.heading) % 360

        if self.x-self.radius > bound_x:
            self.x = 0
        elif self.x+self.radius < 0:
            self.x = bound_x
        if self.y-self.radius > bound_y:
            self.y = 0
        elif self.y+self.radius < 0:
            self.y = bound_y
        
        self.y += self.dy
        self.x += self.dx

        pg.draw.circle(surface, (255, 255, 255), (self.x, self.y), self.radius, 30)

class UFO:
    ...

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
    TIMER_LENGTH = 0

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
    NUM_SHIPS = 4
    PLAYING_FIELD_SIZE = -1
    STEP_INTERVAL = 0.15
    INITIAL_DIFFICULTY = 1
    DIFFICULTY_GAP = 6
    DIFFICULTY_CAP = 25

    TRASH_MODE = True

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.console_update = console_update
        should_quit = self.console_update()
        if should_quit: return
    
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers
      
        self.rock_speed = 10
        self.fpscap = 60
        self.player_speed = 8
        self.bullet_speed = 18

        if self.TRASH_MODE:
            self.rock_speed = 36
            self.fpscap = 8
            self.player_speed = 30
            self.bullet_speed = 67


        self.main_menu = MainMenu(self.display_surf, self.console_update, self.controllers)
        self.difficulty = self.INITIAL_DIFFICULTY
        self.num_asteroids: float = 0

        self.screens = [Screen(pg.Rect(0, 0, self.WIDTH, self.HEIGHT), pg.SRCALPHA)]
        self.clock = pg.time.Clock()
        self.A_Pressed = False

        self.ships = [Ship((randint(0, 69), randint(0, 69)), SHIP_COLOURS[i], self.player_speed) for i in range(self.NUM_SHIPS)]
        self.bullets = []
        self.asteroids = []

        self.last_snake_move_time = time()
        self.last_difficulty_increase = time()

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

        cont_lbl = self.main_menu.fonts["large"].render("Press START to play again...", True, (255, 255, 255))
        cont_lbl.blit(self.main_menu.fonts["large"].render("      START", True, (255, 0, 255)))
        men_lbl = self.main_menu.fonts["large"].render("Press B to edit settings.", True, (255, 255, 255))
        men_lbl.blit(self.main_menu.fonts["large"].render("      B", True, (255, 255, 0)))

        def reset_game() -> None:
            self.__init__(self.display_surf, self.console_update, self.get_num_players, self.controllers)

        while 1:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        reset_game()
                        return

            for event in pg.event.get():
                pass

            self.display_surf.blit(cont_lbl, (self.WIDTH // 2 - cont_lbl.width // 2, curr_y + 40))
            self.display_surf.blit(men_lbl, (self.WIDTH // 2 - men_lbl.width // 2, curr_y + 100))

            for controller in self.controllers:
                for event in controller.event.get():
                    if event.type == CONTROLS.START:
                        reset_game()
                        return
                    if event.type== CONTROLS.ABXY.B:
                        reset_game()
                        return

            self.console_update()

            pg.display.flip()

    def main(self) -> None:
        while 1:
            
            self.clock.tick(self.fpscap)

            for screen in self.screens:
                screen.fill((0, 0, 0))

            if time() - self.last_difficulty_increase >= self.DIFFICULTY_GAP:
                if self.difficulty < self.DIFFICULTY_CAP:
                    self.difficulty += 1
                self.last_difficulty_increase = time()
                #print(self.difficulty)

            #spawn "meteors"
            if self.num_asteroids < self.difficulty:
                self.num_asteroids += 1
                self.asteroids.append(Rock(76, 500, 500, self.rock_speed, randint(1, 358)))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pass
                
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_a:
                        #shoot bullet
                        self.bullets.append(Bullet(self.ships[0].nozzle, self.ships[0].color, self.ships[0].direction, self.bullet_speed))
                    elif event.key == pg.K_n:
                        #shoot bullet
                        self.bullets.append(Bullet(self.ships[1].nozzle, self.ships[1].color, self.ships[1].direction, self.bullet_speed))
                    elif event.key == pg.K_y:
                        self.ships[0].dead = True
            
            keys = pg.key.get_pressed()
            if keys[pg.K_UP]:
                self.ships[0].move_up()
            elif keys[pg.K_RIGHT]:
                self.ships[0].move_right()
            elif keys[pg.K_DOWN]:
                self.ships[0].move_down()
            elif keys[pg.K_LEFT]:
                self.ships[0].move_left()

            if keys[pg.K_u]:
                self.ships[1].move_up()
            elif keys[pg.K_k]:
                self.ships[1].move_right()
            elif keys[pg.K_j]:
                self.ships[1].move_down()
            elif keys[pg.K_h]:
                self.ships[1].move_left()

            should_quit = self.console_update()
            if should_quit: return
            
            for c, controller in enumerate(self.controllers):
                stilla = False
                for event in controller.event.get():
                    if event.type == CONTROLS.DPAD.UP:
                        self.ships[c].move_up()
                    elif event.type == CONTROLS.DPAD.RIGHT:
                        self.ships[c].move_right()
                    elif event.type == CONTROLS.DPAD.DOWN:
                        self.ships[c].move_down()
                    elif event.type == CONTROLS.DPAD.LEFT:
                        self.ships[c].move_left()
                    
                    if event.type == CONTROLS.ABXY.A:
                        if self.ships[c].apressed == False:
                            self.ships[c].apressed == True
                            self.bullets.append(Bullet(self.ships[0].nozzle, self.ships[0].color, self.ships[0].direction, self.bullet_speed))
                        stilla = True

                if controller.plugged_in and not stilla:
                    self.ships[c].apressed = False



            #doing the thing with the thing 
            #collisoas
            for i, rock in enumerate(self.asteroids):
                for i2, bullet in enumerate(self.bullets):
                    if ((bullet.x > rock.x - rock.radius) and (bullet.x < rock.x + rock.radius)) and ((bullet.y > rock.y - rock.radius) and (bullet.y < rock.y + rock.radius)):
                        if rock.big == True:
                            self.asteroids.append(Rock(38, rock.x, rock.y, rock.speed, rock.heading+randint(-35, 35), False))
                            self.asteroids.append(Rock(38, rock.x, rock.y, rock.speed, (360-rock.heading)+randint(-35, 35), False))
                        else:
                            self.num_asteroids -= 0.5
                        self.asteroids.pop(i)
                        self.bullets.pop(i2)
                        self.ships[0].score += 1

            #drawaing and moving
            for ship in self.ships:
                for rock in self.asteroids:
                    for point in ship.tripoints:
                        if ((point[0] > rock.x - rock.radius) and (point[0] < rock.x + rock.radius)) and ((point[1] > rock.y - rock.radius) and (point[1] < rock.y + rock.radius)):
                            ship.dead = True
                #print(ship.x, ship.y)
                ship.draw(self.display_surf)
            for bullet in self.bullets:
                bullet.move(self.display_surf)
            for rock in self.asteroids:
                rock.move(self.display_surf, 1920, 1080)

            if time() - self.last_snake_move_time > self.STEP_INTERVAL:
                self.last_snake_move_time = time()

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

            self.display_surf.blit(self.main_menu.fonts["large"].render(f"Level: {self.difficulty}", True, (0, 255, 0)))
            self.display_surf.blit(self.main_menu.fonts["large"].render(f"Score: {self.ships[0].score}", True, (250, 156, 28)), (900, 0))

            self.console_update()

            pg.display.flip()

            for screen in self.screens:
                self.display_surf.blit(screen, screen.pos)