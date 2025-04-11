#code "borrowed" from /Games/Snither/main.py
#remember to probably add multiple lives
import pygame as pg
from Console.UI.pygame_gui import Button

from Console.Controllers.controller import Controller, CONTROLS
from Console.sound import generate_square_wave, generate_sine_wave

from time import time
from random import randint
from math import cos, sin, radians, sqrt

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

def is_point_inside_triangle(px, py, tripoints):
    # Triangle vertices
    x1, y1 = tripoints[0]
    x2, y2 = tripoints[1]
    x3, y3 = tripoints[2]

    # Calculate the area of the main triangle
    def area(x1, y1, x2, y2, x3, y3):
        return abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2)) / 2

    area_main = area(x1, y1, x2, y2, x3, y3)

    # Calculate the areas of the three smaller triangles formed with the point (px, py)
    area1 = area(px, py, x2, y2, x3, y3)
    area2 = area(x1, y1, px, py, x3, y3)
    area3 = area(x1, y1, x2, y2, px, py)

    # If the sum of the areas of the smaller triangles equals the area of the main triangle, the point is inside
    return area1 + area2 + area3 == area_main

class DIRECTION:
    UP    = 1
    RIGHT = 4
    DOWN  = 2
    LEFT  = 3

    @property
    def RANDOM(self) -> int: return randint(1, 4)

class Bullet:
    def __init__(self, location: Tuple[int, int], color: pg.Color, direction: int, speed: int, player: int|None):
        self.x = location[0]
        self.y = location[1]
        self.color = color
        self.speed = speed
        self.direction = direction
        self.player = player

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
        self.abing = 10

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
    def __init__(self, x, y, speed):
        self.speed = speed*0.75
        self.scale = 25
        self.x = x
        self.y = y
        self.dangerzone = 750
        self.bullets: List[Bullet] = []
        self.cooldown = 1
        self.quadpoints = [(3*self.scale+self.x, 1*self.scale+self.y), (1*self.scale+self.x, 3*self.scale+self.y), (3*self.scale+self.x, 5*self.scale+self.y), (5*self.scale+self.x, 3*self.scale+self.y)]
    
    def shoot(self):
        self.bullets.append(Bullet((3*self.scale+self.x, 1*self.scale+self.y), (250, 156, 28), 1, 18, None))
        self.bullets.append(Bullet((1*self.scale+self.x, 3*self.scale+self.y), (250, 156, 28), 3, 18, None))
        self.bullets.append(Bullet((3*self.scale+self.x, 5*self.scale+self.y), (250, 156, 28), 2, 18, None))
        self.bullets.append(Bullet((5*self.scale+self.x, 3*self.scale+self.y), (250, 156, 28), 4, 18, None))
    
    def ai(self, surface, bound_x: int, bound_y: int, player_locations: List[tuple]):
        if self.x < 5:
            self.x += self.speed/2
        elif self.x > bound_x - -5:
            self.x -= self.speed
        elif self.y < 5:
            self.y -= self.speed
        elif self.y > bound_y -5:
            self.y += self.speed
        else:
            closestlocation = (0, 0)
            closestdistance = 100000
            for location in player_locations:
                d = sqrt((location[0]-self.x)**2 + (location[1]-self.y)**2)
                if d < closestdistance:
                    closestlocation = location
                    closestdistance = d
            
            self.cooldown -= 1
            if self.cooldown == 0:
                self.cooldown = 10

            if closestdistance < self.dangerzone and self.cooldown == 4:
                self.shoot()

            # Check if the closest distance is greater than a third of the danger zone
            if closestdistance > self.dangerzone / 1.5:
                horizontal_distance = abs(closestlocation[0] - self.x)
                vertical_distance = abs(closestlocation[1] - self.y)
            
                # Prioritize alignment on the x-axis first
                if horizontal_distance > vertical_distance:
                    # Try to align on the x-axis, move horizontally
                    if closestlocation[0] > self.x:
                        self.x += self.speed
                    elif closestlocation[0] < self.x:
                        self.x -= self.speed
                    
                    # After moving on the x-axis, adjust the y-axis to avoid getting too close
                    if closestdistance > self.dangerzone / 1.5:  # Ensure no breaking the danger zone
                        if closestlocation[1] > self.y:
                            self.y += self.speed
                        elif closestlocation[1] < self.y:
                            self.y -= self.speed
                else:
                    # Try to align on the y-axis, move vertically
                    if closestlocation[1] > self.y:
                        self.y += self.speed
                    elif closestlocation[1] < self.y:
                        self.y -= self.speed
            
                    # After moving on the y-axis, adjust the x-axis to avoid getting too close
                    if closestdistance > self.dangerzone / 1.5:  # Ensure no breaking the danger zone
                        if closestlocation[0] > self.x:
                            self.x += self.speed
                        elif closestlocation[0] < self.x:
                            self.x -= self.speed




        pg.draw.polygon(surface, (250, 156, 28), [(3*self.scale+self.x, 1*self.scale+self.y), (1*self.scale+self.x, 3*self.scale+self.y), (3*self.scale+self.x, 5*self.scale+self.y), (5*self.scale+self.x, 3*self.scale+self.y)])
        self.quadpoints = [(3*self.scale+self.x, 1*self.scale+self.y), (1*self.scale+self.x, 3*self.scale+self.y), (3*self.scale+self.x, 5*self.scale+self.y), (5*self.scale+self.x, 3*self.scale+self.y)]
        

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
    TIMER_LENGTH = 5

    def __init__(self, display_surf: pg.Surface, console_update: object, controllers: List[Controller], num_players:int, autostart) -> None:
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

        for i in range(num_players):
            self.players[i].controller.plugged_in = True

        if autostart == True:
            return self.main(True)
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

    def main(self, autostart=False) -> None:
        if autostart: self.start_game = True
        while not self.start_game:
            self.display_surf.fill((0, 0, 0))
            self.clock.tick(60)

            for i, controller in enumerate(self.controllers):
                for event in controller.event.get():
                    if event.type == CONTROLS.ABXY.A:
                        self.players[i].ready = not self.players[i].ready
            
            for event in pg.event.get():    
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.players[0].ready = not self.players[0].ready
                        self.players[1].ready = not self.players[1].ready
                        self.players[2].ready = not self.players[2].ready
                        self.players[3].ready = not self.players[3].ready

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
    NUM_SHIPS = 2
    PLAYING_FIELD_SIZE = -1
    STEP_INTERVAL = 0.15
    INITIAL_DIFFICULTY = 1
    DIFFICULTY_GAP = 6
    DIFFICULTY_CAP = 25
    TRASH_MODE = True
    SET_FPS = 8


    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller], autostart=False) -> None:
        self.console_update = console_update
        should_quit = self.console_update()
        if should_quit: return
    
        self.display_surf = display_surf
        self.console_update = console_update
        self.controllers = controllers
        self.NUM_SHIPS = 4#get_num_players()
        self.get_num_p = lambda: self.NUM_SHIPS
      
        self.rock_speed = 10
        self.fpscap = 60
        self.player_speed = 8
        self.bullet_speed = 18

        if self.TRASH_MODE:
            self.fpscap = self.SET_FPS
            self.rock_speed = ((10*60)/self.fpscap)/2
            self.player_speed = ((8*60)/self.fpscap)/2
            self.bullet_speed = ((18*60)/self.fpscap)/2


        self.main_menu = MainMenu(self.display_surf, self.console_update, self.controllers, self.NUM_SHIPS, autostart)
        self.difficulty = self.INITIAL_DIFFICULTY
        self.num_asteroids: float = 0

        self.screens = [Screen(pg.Rect(0, 0, self.WIDTH, self.HEIGHT), pg.SRCALPHA)]
        self.clock = pg.time.Clock()
        self.A_Pressed = False
        if self.NUM_SHIPS > 0:
            self.ships = [Ship((randint(0, 69), randint(0, 69)), SHIP_COLOURS[i], self.player_speed) for i in range(self.NUM_SHIPS)]
        else:
            self.ships = [Ship((randint(0, 69), randint(0, 69)), SHIP_COLOURS[2], self.player_speed)]
            self.ships[0].dead = True
            #self.NUM_SHIPS = 1
            #print(self.ships)
        self.bullets = []
        self.asteroids = []
        self.UFOs: List[UFO] = []

        self.UFOactive = randint(3, 14)

        self.last_snake_move_time = time()
        self.last_difficulty_increase = time()

        self.display_surf.fill((0, 0, 0))

        self.main()

    def show_game_over(self, alive_snake_index: int | None) -> None:
        self.display_surf.fill((0, 0, 0, 128))

        go_lbl = self.main_menu.fonts["large"].render("Game Over!", True, (255, 255, 255))
        self.display_surf.blit(go_lbl, (self.WIDTH // 2 - go_lbl.width // 2, 100))

        winner_lbl = self.main_menu.fonts["medium"].render(f"Player {alive_snake_index + 1} scored the most!", True, (255, 255, 255))
        winner_lbl.blit(self.main_menu.fonts["medium"].render(f" " * len(f"Player {alive_snake_index + 1} ") + "scored", True, (255, 150, 0)), (0, 0))

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

        def reset_game(autostart: bool) -> None:
            self.__init__(self.display_surf, self.console_update, self.get_num_p, self.controllers, autostart)

        while 1:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        reset_game(True)
                        return
                    elif event.key == pg.K_BACKSPACE:
                        reset_game(False)
                        return

            for event in pg.event.get():
                pass

            self.display_surf.blit(cont_lbl, (self.WIDTH // 2 - cont_lbl.width // 2, curr_y + 40))
            self.display_surf.blit(men_lbl, (self.WIDTH // 2 - men_lbl.width // 2, curr_y + 100))

            for controller in self.controllers:
                for event in controller.event.get():
                    if event.type == CONTROLS.START:
                        reset_game(True)
                        return
                    if event.type== CONTROLS.ABXY.B:
                        reset_game(False)
                        return

            self.console_update()

            pg.display.flip()

    def main(self) -> None:
        while 1:
            
            self.clock.tick(self.fpscap)
            #print(self.clock.get_fps())

            for screen in self.screens:
                screen.fill((0, 0, 0))

            if time() - self.last_difficulty_increase >= self.DIFFICULTY_GAP:
                if self.difficulty < self.DIFFICULTY_CAP:
                    self.difficulty += 1
                    if self.difficulty == self.UFOactive:
                        self.UFOs.append(UFO(-50, 500, self.player_speed*2))
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
                    #if event.key == pg.K_a:
                    #    #shoot bullet
                    #    self.bullets.append(Bullet(self.ships[0].nozzle, self.ships[0].color, self.ships[0].direction, self.bullet_speed, 0))
                    if event.key == pg.K_n:
                        #shoot bullet
                        self.bullets.append(Bullet(self.ships[1].nozzle, self.ships[1].color, self.ships[1].direction, self.bullet_speed, 1))
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
            if keys[pg.K_a]:
                self.bullets.append(Bullet(self.ships[0].nozzle, self.ships[0].color, self.ships[0].direction, self.bullet_speed, 0))

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
            
            for c in range(self.NUM_SHIPS):
                controller = self.controllers[c]
                for event in controller.event.get():
                    if event.type == CONTROLS.DPAD.UP:
                        self.ships[c].move_up()
                    elif event.type == CONTROLS.DPAD.RIGHT:
                        self.ships[c].move_right()
                    elif event.type == CONTROLS.DPAD.DOWN:
                        self.ships[c].move_down()
                    elif event.type == CONTROLS.DPAD.LEFT:
                        self.ships[c].move_left()
                    
                    if self.ships[c].abing != 0:
                        self.ships[c].abing -= 1
                    
                    if self.ships[c].abing == 0 and event.type == CONTROLS.ABXY.A:
                        self.bullets.append(Bullet(self.ships[c].nozzle, self.ships[c].color, self.ships[c].direction, self.bullet_speed, c))
                        self.ships[c].abing = 4

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
                        self.ships[bullet.player].score += 1
                        self.bullets.pop(i2)

            for i, ufo in enumerate(self.UFOs):
                for i2, bullet in enumerate(self.bullets):
                    if is_point_inside_triangle(bullet.x, bullet.y, [ufo.quadpoints[0], ufo.quadpoints[1], ufo.quadpoints[2]]) or is_point_inside_triangle(bullet.x, bullet.y, [ufo.quadpoints[2], ufo.quadpoints[3], ufo.quadpoints[1]]):
                        self.bullets.pop(i2)
                        self.UFOs.pop(i)

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
            for ufo in self.UFOs:
                ufo.ai(self.display_surf, 1920, 1080, [(p.x, p.y) for p in self.ships if not p.dead])
                for b in ufo.bullets:
                    b.move(self.display_surf)
                    for ship in self.ships:
                        if is_point_inside_triangle(b.x, b.y, ship.tripoints):
                            ship.dead = True

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

            total_texts = self.NUM_SHIPS 
            
            available_space = self.display_surf.get_width()
            space_between_texts = (available_space- total_texts) / (total_texts + 1)
            offset = space_between_texts/10
            
            # Display the first text (e.g., Level)
            self.display_surf.blit(self.main_menu.fonts["large"].render(f"Level: {self.difficulty}", True, (250, 156, 28)), (0, 0))
            
            # Display additional text for each ship's score
            for i in range(self.NUM_SHIPS):
                x_pos = (i + 1) * space_between_texts + (i + 1)
                self.display_surf.blit(self.main_menu.fonts["large"].render(f"Score: {self.ships[i].score}", True, SHIP_COLOURS[i]), (x_pos, 0))
            

            #self.console_update()

            pg.display.flip()

            for screen in self.screens:
                self.display_surf.blit(screen, screen.pos)