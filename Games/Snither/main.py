import pygame as pg

from Console.Controllers.controller import Controller, CONTROLS
from Console.sound import generate_square_wave, generate_sine_wave

from time import time
from random import randint

from typing import Sequence, List, Tuple, Dict

startup_txt = """
   _____       _ _   _               
  / ____|     (_) | | |              
 | (___  _ __  _| |_| |__   ___ _ __ 
  \___ \| '_ \| | __| '_ \ / _ \ '__|
  ____) | | | | | |_| | | |  __/ |   
 |_____/|_| |_|_|\__|_| |_|\___|_|   
 
"""

print(startup_txt)

pg.init()

FONTS_PATH = "./UI/Fonts"

class DIRECTION:
    UP    = 0
    RIGHT = 1
    DOWN  = 2
    LEFT  = 3

    @staticmethod
    def random() -> int: return randint(0, 3)

class Apple:
    SIZE = 50
    COLOR = (0, 255, 0)

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def draw(self, surface: pg.Surface, surface_rect: pg.Rect) -> None:
        pg.draw.rect(surface, (self.COLOR), pg.Rect(self.x * self.SIZE - self.SIZE // 2 - surface_rect.x, self.y * self.SIZE - self.SIZE // 2 - surface_rect.y, self.SIZE, self.SIZE))

class Snake:
    PART_SIZE = 50
    ACTIVATION_PERCENT = 0.5

    def __init__(self, head: Sequence[int], game_board: List[List[int]], apple_board: List[List[int]], color: pg.Color, apples: List[Apple], is_player: bool, deaths: int = 0) -> None:
        self.game_board = game_board
        self.apple_board = apple_board
        self.direction = DIRECTION.random()
        self.body = [head]

        self.color = color
        self.og_color = color
        self.apples = apples
        self.is_player = is_player

        self.game_board[self.y][self.x] = 1
        self.last_update_direction = self.direction
        self.dead = False
        self.deaths = deaths

        self.last_tail_position = [self.body[-1][0], self.body[-1][1]]

        self.grow_sound = generate_sine_wave(500, 0.2, volume=0.04)

        self.grow()
        self.grow()
        self.grow()

    @property
    def head(self) -> Sequence[int]:
        return self.body[0]

    @property
    def tail(self) -> Sequence[int]:
        return self.body[-1]

    @property
    def x(self) -> int: return self.head[0]

    @property
    def y(self) -> int: return self.head[1]

    @property
    def name_prefix(self) -> str:
        if self.is_player: return "Player"
        else: return "Bot"

    def move(self) -> None:
        if self.dead: return

        self.game_board[self.tail[1]][self.tail[0]] = 0

        head = self.head
        self.last_tail_position = [self.tail[0], self.tail[1]]

        match self.direction:
            case DIRECTION.UP:    head = [head[0],     head[1] - 1]
            case DIRECTION.RIGHT: head = [head[0] + 1, head[1]]
            case DIRECTION.DOWN:  head = [head[0],     head[1] + 1]
            case DIRECTION.LEFT:  head = [head[0] - 1, head[1]]

        for i in range(len(self.body) - 1, -1, -1): # Skip the first one
            self.body[i] = self.body[i-1].copy()

        self.body[0] = head

        if self.game_board[head[1]][head[0]] == 1:
            self.die()
            return

        self.game_board[self.y][self.x] = 1

        apples_to_remove = []
        for apple in self.apples:
            if self.x == apple.x and self.y == apple.y:
                apples_to_remove.append(apple)
                self.grow(play_sound=True)

        for dead_apple in apples_to_remove:
            self.apples.remove(dead_apple)
            self.apple_board[dead_apple.y][dead_apple.x] = 0

        self.last_update_direction = self.direction

    def die(self) -> None:
        self.dead = True
        self.deaths += 1
        self.color = pg.Color(150, 150, 150)

        if self.is_player:
            generate_square_wave(50, 0.2, volume=0.04).play()

        for part in self.body:
            if part[0] != 0 and part[0] != len(self.game_board) - 1 and part[1] != 0 and part[1] != len(self.game_board) - 1:
                self.game_board[part[1]][part[0]] = 0
                self.apples.append(Apple(part[0], part[1]))

    def grow(self, play_sound: bool = False) -> None:
        self.body.append(self.last_tail_position)

        self.game_board[self.tail[1]][self.tail[0]] = 1

        if play_sound and self.is_player:
            self.grow_sound.play()

    def draw(self, surface: pg.Surface, surface_rect: pg.Rect) -> None:
        for part in self.body:
            if not surface_rect.colliderect(pg.Rect(part[0] * self.PART_SIZE - self.PART_SIZE // 2, part[1] * self.PART_SIZE - self.PART_SIZE // 2, self.PART_SIZE, self.PART_SIZE)): continue

            pg.draw.rect(surface, self.color, (part[0] * self.PART_SIZE - self.PART_SIZE // 2 - surface_rect.x, part[1] * self.PART_SIZE - self.PART_SIZE // 2 - surface_rect.y, self.PART_SIZE * 0.9, self.PART_SIZE * 0.9))

        pg.draw.rect(surface, (255, 255, 255), (self.x * self.PART_SIZE - self.PART_SIZE // 2 - surface_rect.x, self.y * self.PART_SIZE - self.PART_SIZE // 2 - surface_rect.y, self.PART_SIZE * 0.9, self.PART_SIZE * 0.9))

    def face_up(self) -> None:
        if self.last_update_direction == DIRECTION.DOWN: return
        self.direction = DIRECTION.UP

    def face_right(self) -> None:
        if self.last_update_direction == DIRECTION.LEFT: return
        self.direction = DIRECTION.RIGHT

    def face_down(self) -> None:
        if self.last_update_direction == DIRECTION.UP: return
        self.direction = DIRECTION.DOWN

    def face_left(self) -> None:
        if self.last_update_direction == DIRECTION.RIGHT: return
        self.direction = DIRECTION.LEFT

    def turn_left(self) -> None:
        if self.direction == DIRECTION.UP: self.face_left()
        elif self.direction == DIRECTION.RIGHT: self.face_up()
        elif self.direction == DIRECTION.DOWN: self.face_right()
        elif self.direction == DIRECTION.LEFT: self.face_down()

    def turn_right(self) -> None:
        if self.direction == DIRECTION.UP: self.face_right()
        elif self.direction == DIRECTION.RIGHT: self.face_down()
        elif self.direction == DIRECTION.DOWN: self.face_left()
        elif self.direction == DIRECTION.LEFT: self.face_up()

    def ai_move(self) -> None:
        if self.dead: return

        turn_right_percent = 0
        turn_left_percent = 0
        turn_away_percent = 0

        if self.direction == DIRECTION.UP or self.direction == DIRECTION.DOWN:
            # looking left
            for x in range(1, 6):
                nx = max(0, min(self.x-x, len(self.game_board)-1))
                if self.game_board[self.y][nx] == 1:
                    turn_right_percent += (1/5) * (-x) + 1.2 # Worked in desmos so will work here???

            for x in range(1, 6):
                nx = max(0, min(self.x+x, len(self.game_board)-1))
                if self.game_board[self.y][nx] == 1:
                    turn_left_percent += (-(1/5)) * x + 1.2 # Worked in desmos so will work here???

            if self.direction == DIRECTION.UP:
                for y in range(1, 6):
                    ny = max(0, min(self.y-y, len(self.game_board)-1))
                    if self.game_board[ny][self.x] == 1:
                        turn_away_percent += (1/5) * (-y) + 1.2 # Worked in desmos so will work here???
            else:
                for y in range(1, 6):
                    ny = max(0, min(self.y+y, len(self.game_board)-1))
                    if self.game_board[ny][self.x] == 1:
                        turn_away_percent += (-(1/5)) * y + 1.2 # Worked in desmos so will work here???
                    
        else:
            for y in range(1, 6):
                ny = max(0, min(self.y-y, len(self.game_board)-1))
                if self.game_board[ny][self.x] == 1:
                    turn_right_percent += (1/5) * (-y) + 1.2 # Worked in desmos so will work here???

            for y in range(1, 6):
                ny = max(0, min(self.y+y, len(self.game_board)-1))
                if self.game_board[ny][self.x] == 1:
                    turn_left_percent += (-(1/5)) * y + 1.2 # Worked in desmos so will work here???

            if self.direction == DIRECTION.LEFT:
                for x in range(1, 6):
                    nx = max(0, min(self.x-x, len(self.game_board)-1))
                    if self.game_board[self.y][nx] == 1:
                        turn_away_percent += (1/5) * (-x) + 1.2 # Worked in desmos so will work here???
            else:
                for x in range(1, 6):
                    nx = max(0, min(self.x+x, len(self.game_board)-1))
                    if self.game_board[self.y][nx] == 1:
                        turn_away_percent += (-(1/5)) * x + 1.2 # Worked in desmos so will work here???

        if self.direction == DIRECTION.DOWN or self.direction == DIRECTION.LEFT:
            old_turn_right_percent = turn_right_percent
            turn_right_percent = turn_left_percent
            turn_left_percent = old_turn_right_percent

        if turn_away_percent > self.ACTIVATION_PERCENT:
            if turn_right_percent > turn_left_percent:
                turn_right_percent += turn_away_percent
            elif turn_left_percent > turn_right_percent:
                turn_left_percent += turn_away_percent
            else:
                if randint(0, 1) == 0: turn_left_percent += turn_away_percent
                else: turn_right_percent += turn_away_percent

        if turn_right_percent >= self.ACTIVATION_PERCENT:
            if turn_left_percent >= self.ACTIVATION_PERCENT:
                if turn_left_percent > turn_right_percent:
                    self.turn_left()
                    return

            self.turn_right()
            return

        if turn_left_percent >= self.ACTIVATION_PERCENT:
            self.turn_left()
            return

        apple_turn_right_percent = 0.0
        apple_turn_left_percent = 0.0
        apple_turn_towards_percent = 0.0
        
        if self.direction == DIRECTION.UP or self.direction == DIRECTION.DOWN:
            for x in range(1, 6):
                nx = max(0, min(self.x-x, len(self.apple_board)-1))
                if self.apple_board[self.y][nx] == 1:
                    apple_turn_left_percent += (1/5) * (-x) + 1.2 # Worked in desmos so will work here???

            for x in range(1, 6):
                nx = max(0, min(self.x+x, len(self.apple_board)-1))
                if self.apple_board[self.y][nx] == 1:
                    apple_turn_right_percent += (-(1/5)) * x + 1.2 # Worked in desmos so will work here???

            if self.direction == DIRECTION.UP:
                for y in range(1, 6):
                    ny = max(0, min(self.y-y, len(self.apple_board)-1))
                    if self.apple_board[ny][self.x] == 1:
                        apple_turn_towards_percent -= (1/5) * (-y) + 1.2 # Worked in desmos so will work here???
            else:
                for y in range(1, 6):
                    ny = max(0, min(self.y+y, len(self.apple_board)-1))
                    if self.apple_board[ny][self.x] == 1:
                        apple_turn_towards_percent -= (-(1/5)) * y + 1.2 # Worked in desmos so will work here???

        else:
            for y in range(1, 6):
                ny = max(0, min(self.y-y, len(self.apple_board)-1))
                if self.apple_board[ny][self.x] == 1:
                    apple_turn_left_percent += (1/5) * (-y) + 1.2 # Worked in desmos so will work here???

            for y in range(1, 6):
                ny = max(0, min(self.y+y, len(self.apple_board)-1))
                if self.apple_board[ny][self.x] == 1:
                    apple_turn_right_percent += (-(1/5)) * y + 1.2 # Worked in desmos so will work here???

            if self.direction == DIRECTION.LEFT:
                for x in range(1, 6):
                    nx = max(0, min(self.x-x, len(self.apple_board)-1))
                    if self.apple_board[self.y][nx] == 1:
                        apple_turn_towards_percent -= (1/5) * (-x) + 1.2 # Worked in desmos so will work here???
            else:
                for x in range(1, 6):
                    nx = max(0, min(self.x+x, len(self.apple_board)-1))
                    if self.apple_board[self.y][nx] == 1:
                        apple_turn_towards_percent -= (-(1/5)) * x + 1.2 # Worked in desmos so will work here???

        if self.direction == DIRECTION.DOWN or self.direction == DIRECTION.LEFT:
            old_apple_turn_right_percent = turn_right_percent
            apple_turn_right_percent = apple_turn_left_percent
            apple_turn_left_percent = old_apple_turn_right_percent

        if apple_turn_right_percent > turn_left_percent:
            if apple_turn_left_percent > turn_right_percent:
                if apple_turn_left_percent > apple_turn_right_percent:
                    self.turn_left()
                    return

            self.turn_right()
            return

        if apple_turn_left_percent > turn_right_percent:
            self.turn_left()
            return
        
        if randint(0, 4) == 1:
            if randint(0, 1) == 0: self.turn_left()
            else: self.turn_right()


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
        self.last_select_time = 0

    @property
    def ready_text(self) -> str:
        if not self.controller.plugged_in: return "❓" # Should come out as ascii red question mark in the font (null character)
        if self.ready: return "Ready"
        else: return "Not ready"

    @property
    def ready_color(self) -> str:
        if not self.controller.plugged_in: return pg.Color(255, 0, 0)
        if self.ready: return pg.Color(0, 255, 0)
        else: return pg.Color(255, 0, 0)

class MainMenu:
    TIMER_LENGTH = 6

    def __init__(self, display_surf: pg.Surface, console_update: object, controllers: List[Controller], infinite: bool = False) -> None:
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

        self.title_lbl = self.fonts["large"].render("Snither", True, (255, 255, 255))

        self.info_lbl = self.fonts["medium"].render   ("Press A to ready / unready...", True, (255, 255, 255))
        self.info_lbl.blit(self.fonts["medium"].render("      A", True, (0, 255, 0)))

        self.timer_active = False
        self.timer_start_time = time()
        self.start_game = False
        self.last_timer_time = 0
        self.timer_first_beep = True

        self.infinite_mode_enabled_lbl = self.fonts["medium"].render("Infinite mode enabled... (B)", True, (255, 255, 255))
        self.infinite_mode_enabled_lbl.blit(self.fonts["medium"].render(" " * len("Infinite mode ") + "enabled", True, (0, 255, 0)), (0, 0))
        self.infinite_mode_enabled_lbl.blit(self.fonts["medium"].render(" " * len("Infinite mode enabled... (") + "B", True, (255, 180, 0)), (0, 0))

        self.infinite_mode_disabled_lbl = self.fonts["medium"].render("Infinite mode disabled... (B)", True, (255, 255, 255))
        self.infinite_mode_disabled_lbl.blit(self.fonts["medium"].render(" " * len("Infinite mode ") + "disabled", True, (255, 0, 0)), (0, 0))
        self.infinite_mode_disabled_lbl.blit(self.fonts["medium"].render(" " * len("Infinite mode disabled... (") + "B", True, (255, 180, 0)), (0, 0))

        self.timer_start_lbl = self.fonts["medium"].render("Game starting in  ...", True, (255, 255, 255))
        self.timer_end_lbls = [self.fonts["medium"].render(f"                 {i}", True, (0, 0, 255)) for i in range(1, self.TIMER_LENGTH + 1)]

        #self.players[0].controller.plugged_in = True
        #self.players[1].ready = True
        #self.players[1].controller.plugged_in = True
        #self.players[2].ready = True
        #self.players[2].controller.plugged_in = True
        #self.players[3].ready = True
        #self.players[3].controller.plugged_in = True

        self.infinite = infinite

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
        num_players = 0

        for player in self.players:
            if player.controller.plugged_in and not player.ready:
                self.reset_timer()
                return
            elif player.controller.plugged_in:
                num_players += 1

        if num_players == 0:
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
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.players[0].ready = not self.players[0].ready

                    elif event.key == pg.K_b:
                        if self.timer_active: continue

                        self.infinite = not self.infinite

            for i, controller in enumerate(self.controllers):
                for event in controller.event.get():
                    # Dont have this outside the event loop because it will 'queue' events
                    if time() - self.players[i].last_select_time < 0.3: continue

                    if event.type == CONTROLS.START:
                        controller.plugged_in = not controller.plugged_in
                        self.players[i].ready = False
                        self.players[i].last_select_time = time()

                    elif event.type == CONTROLS.ABXY.A:
                        if not controller.plugged_in: continue

                        self.players[i].ready = not self.players[i].ready
                        self.players[i].last_select_time = time()

                    elif event.type == CONTROLS.ABXY.B:
                        if not controller.plugged_in: continue
                        if self.timer_active: continue

                        self.infinite = not self.infinite
                        self.players[i].last_select_time = time()

            self.draw_player_buttons()

            self.display_surf.blit(self.title_lbl, (self.width // 2 - self.title_lbl.width // 2, 100))

            if self.infinite:
                self.display_surf.blit(self.infinite_mode_enabled_lbl, (self.width // 2 - self.infinite_mode_enabled_lbl.width // 2, self.height - 250))
            else:
                self.display_surf.blit(self.infinite_mode_disabled_lbl, (self.width // 2 - self.infinite_mode_disabled_lbl.width // 2, self.height - 250))
            
            if self.timer_active:
                timer_time = self.TIMER_LENGTH - (time() - self.timer_start_time)

                if self.last_timer_time != int(round(timer_time, 0)):
                    if self.timer_first_beep:
                        self.timer_first_beep = False
                    else:
                        generate_sine_wave(800, 0.2, volume=0.15).play()

                    self.last_timer_time = int(round(timer_time, 0))

                curr_time_int = max(0, min(int(round(timer_time, 0)), len(self.timer_end_lbls) - 1))
                self.display_surf.blit(self.timer_start_lbl, (self.width // 2 - self.timer_start_lbl.width // 2, self.height - 150))
                self.display_surf.blit(self.timer_end_lbls[curr_time_int-1], (self.width // 2 - self.timer_start_lbl.width // 2, self.height - 150))
            else:
                self.display_surf.blit(self.info_lbl, (self.width // 2 - self.info_lbl.width // 2, self.height - 150))

            self.check_game_start()

            game_quit = self.console_update()
            if game_quit: return

            pg.display.flip()

class Snither:
    PYGAME_INFO: any = pg.display.Info()
    WIDTH: int = PYGAME_INFO.current_w
    HEIGHT: int = PYGAME_INFO.current_h

    SNAKE_COLORS = {
        0: (255, 0, 0), # Red
        1: (0, 255, 0), # Green
        2: (0, 0, 255), # Blue
        3: (255, 255, 0), # Yellow
        4: (0, 255, 255) # Cyan
    }

    NUM_SNAKES = 15
    NUM_APPLES = 100
    PLAYING_FIELD_SIZE = 4000
    STEP_INTERVAL = 0.15
    MINIMAP_SIZE = 240

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller], infinite: bool = False) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers

        self.main_menu = MainMenu(self.display_surf, self.console_update, self.controllers, infinite)

        should_quit = self.console_update()
        if should_quit: return

        self.num_screens = self.get_num_players()

        self.screens = self.setup_screens()
        self.clock = pg.time.Clock()

        self.game_board = [[0 for x in range(self.PLAYING_FIELD_SIZE // Snake.PART_SIZE)] for y in range(self.PLAYING_FIELD_SIZE // Snake.PART_SIZE)]
        self.apple_board = [[0 for x in range(self.PLAYING_FIELD_SIZE // Snake.PART_SIZE)] for y in range(self.PLAYING_FIELD_SIZE // Snake.PART_SIZE)]

        # Borders
        self.game_board[0] = [1 for x in range(self.PLAYING_FIELD_SIZE // Snake.PART_SIZE)]
        self.game_board[-1] = [1 for x in range(self.PLAYING_FIELD_SIZE // Snake.PART_SIZE)]

        for y in range(len(self.game_board)):
            self.game_board[y][0] = 1
            self.game_board[y][-1] = 1

        self.apples = [Apple(randint(1, len(self.game_board) - 2), randint(1, len(self.game_board) - 2)) for _ in range(self.NUM_APPLES)]

        for apple in self.apples:
            self.apple_board[apple.y][apple.x] = 1

        self.snakes = [Snake([randint(5, len(self.game_board) - 6), randint(5, len(self.game_board) - 6)],
                             self.game_board, self.apple_board, self.SNAKE_COLORS[randint(0, len(self.SNAKE_COLORS) - 1)], self.apples, i <= self.num_screens - 1) for i in range(self.NUM_SNAKES)]

        self.last_snake_move_time = time()

        self.minimap_surf = pg.Surface((self.MINIMAP_SIZE, self.MINIMAP_SIZE))

        self.display_surf.fill((0, 0, 0))

        self.main()

    @property
    def infinite(self) -> bool: return self.main_menu.infinite

    def setup_screens(self) -> List[Screen]:
        def three_screens() -> List[Screen]:
            screen_top_left_rect = pg.Rect(0, 0, self.WIDTH // 2, self.HEIGHT // 2)
            screen_top_right_rect = pg.Rect(self.WIDTH // 2, 0, self.WIDTH // 2, self.HEIGHT // 2)
            screen_bottom_left_rect = pg.Rect(0, self.HEIGHT // 2, self.WIDTH // 2, self.HEIGHT // 2)

            screen_top_left = Screen(screen_top_left_rect, pg.SRCALPHA)
            screen_top_right = Screen(screen_top_right_rect, pg.SRCALPHA)
            screen_bottom_left = Screen(screen_bottom_left_rect, pg.SRCALPHA)

            return [screen_top_left, screen_top_right, screen_bottom_left]

        match self.num_screens:
            case 1: return [Screen(pg.Rect(0, 0, self.WIDTH, self.HEIGHT), pg.SRCALPHA)]
            case 2:
                screen_left_rect = pg.Rect(0, 0, self.WIDTH // 2, self.HEIGHT)
                screen_right_rect = pg.Rect(self.WIDTH // 2, 0, self.WIDTH // 2, self.HEIGHT)

                screen_left = Screen(screen_left_rect, pg.SRCALPHA)
                screen_right = Screen(screen_right_rect, pg.SRCALPHA)

                return [screen_left, screen_right] 

            case 3: return three_screens()
            case 4:
                screens = three_screens()

                screen_bottom_right_rect = pg.Rect(self.WIDTH // 2, self.HEIGHT // 2, self.WIDTH // 2, self.HEIGHT // 2)
                screen_bottom_right = Screen(screen_bottom_right_rect, pg.SRCALPHA)

                screens.append(screen_bottom_right)

                return screens

    def draw_minimap(self) -> None:
        square_size = self.MINIMAP_SIZE / (self.PLAYING_FIELD_SIZE // Snake.PART_SIZE)
        for y in range(len(self.game_board)):
            for x in range(len(self.game_board[y])):
                status = self.game_board[y][x]
                pg.draw.rect(self.minimap_surf, (255*status, 255*status, 255*status), (x*square_size, y*square_size, square_size, square_size))

        if self.num_screens == 1:
            self.display_surf.blit(self.minimap_surf, (self.WIDTH - self.MINIMAP_SIZE - 50, self.HEIGHT - self.MINIMAP_SIZE - 50))
        else:
            self.display_surf.blit(self.minimap_surf, (self.WIDTH // 2 - self.MINIMAP_SIZE // 2, self.HEIGHT // 2 - self.MINIMAP_SIZE // 2))

    def draw_splitscreen_lines(self) -> None:
        if self.num_screens == 1: return

        pg.draw.line(self.display_surf, (255, 255, 255), (self.WIDTH // 2, 0), (self.WIDTH // 2, self.HEIGHT), width=5)

        if self.num_screens >= 3:
            pg.draw.line(self.display_surf, (255, 255, 255), (0, self.HEIGHT // 2), (self.WIDTH, self.HEIGHT // 2), width=5)

    def show_game_over(self, alive_snake_index: int | None, players_alive: bool) -> None:
        self.display_surf.fill((0, 0, 0, 128))

        go_lbl = self.main_menu.fonts["large"].render("Game Over!", True, (255, 255, 255))
        self.display_surf.blit(go_lbl, (self.WIDTH // 2 - go_lbl.width // 2, 100))

        sorted_snakes = sorted(self.snakes, key=lambda snake: len(snake.body), reverse=True)

        best_snake_index = alive_snake_index
        for snake in sorted_snakes:
            if not snake.dead:
                best_snake_index = self.snakes.index(snake)
                break

        if alive_snake_index is not None and players_alive:
            winner_lbl = self.main_menu.fonts["medium"].render(f"{self.snakes[alive_snake_index].name_prefix} {alive_snake_index + 1} won by domination!", True, (255, 255, 255))
            winner_lbl.blit(self.main_menu.fonts["medium"].render(f" " * len(f"{self.snakes[alive_snake_index].name_prefix} {alive_snake_index + 1} won by ") + "domination", True, (255, 150, 0)), (0, 0))
        else:
            winner_snake_index = 0
            for i, snake in enumerate(self.snakes):
                if len(snake.body) > len(self.snakes[winner_snake_index].body):
                    winner_snake_index = i

            winner_lbl = self.main_menu.fonts["medium"].render(f"{self.snakes[best_snake_index].name_prefix} {best_snake_index + 1} won by length!", True, (255, 255, 255))
            winner_lbl.blit(self.main_menu.fonts["medium"].render(f" " * len(f"{self.snakes[best_snake_index].name_prefix} {best_snake_index + 1} won by ") + "length", True, (0, 255, 0)), (0, 0))

        self.display_surf.blit(winner_lbl, (self.WIDTH // 2 - winner_lbl.width // 2, 100 + go_lbl.height + 50))

        scores_lbl = self.main_menu.fonts["large"].render("Scores:", True, (255, 255, 255))
        scores_lbl_y = 100 + go_lbl.height + 50 + winner_lbl.height + 50
        self.display_surf.blit(scores_lbl, (self.WIDTH // 2 - scores_lbl.width // 2, scores_lbl_y))

        curr_y = scores_lbl_y + scores_lbl.height + 20 + 30
        spacing = 40

        score_lbls = []
        width_sum = 0
        for i, snake in enumerate(sorted_snakes):
            if self.infinite:
                score_lbls.append(self.main_menu.fonts["medium"].render(f"{snake.name_prefix} {self.snakes.index(snake) + 1} - {len(snake.body)} - Deaths: {snake.deaths}", True, snake.og_color))
            else:
                score_lbls.append(self.main_menu.fonts["medium"].render(f"{snake.name_prefix} {self.snakes.index(snake) + 1} - {len(snake.body)}", True, snake.og_color))

            width_sum += score_lbls[-1].width

        avg_width = width_sum / len(score_lbls)
        for score_lbl in score_lbls:
            self.display_surf.blit(score_lbl, (self.WIDTH // 2 - avg_width // 2, curr_y))
            curr_y += spacing

        cont_lbl = self.main_menu.fonts["large"].render("Press A to continue...", True, (255, 255, 255))
        cont_lbl.blit(self.main_menu.fonts["large"].render("      A", True, (0, 255, 0)))

        start_time = time()
        continue_timer_length = 3

        def reset_game() -> None:
            if time() - start_time < continue_timer_length: return

            self.__init__(self.display_surf, self.console_update, self.get_num_players, self.controllers, self.infinite)

        while 1:
            self.clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        if time() - start_time < continue_timer_length: continue

                        reset_game()
                        return

            if time() - start_time >= continue_timer_length:
                self.display_surf.blit(cont_lbl, (self.WIDTH // 2 - cont_lbl.width // 2, curr_y + 40))

                for controller in self.controllers:
                    for event in controller.event.get():
                        if event.type == CONTROLS.ABXY.A:
                            reset_game()
                            return

            self.console_update()

            pg.display.flip()

    def main(self) -> None:
        while 1:
            self.clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.snakes[0].face_up()
                    elif event.key == pg.K_RIGHT:
                        self.snakes[0].face_right()
                    elif event.key == pg.K_DOWN:
                        self.snakes[0].face_down()
                    elif event.key == pg.K_LEFT:
                        self.snakes[0].face_left()
                    
                    elif event.key == pg.K_BACKSPACE:
                        if self.infinite:
                            self.show_game_over(None, False)
                            return

            should_quit = self.console_update()
            if should_quit: return

            for c, controller in enumerate(self.controllers):
                for event in controller.event.get():
                    if event.type == CONTROLS.DPAD.UP:
                        self.snakes[c].face_up()
                    elif event.type == CONTROLS.DPAD.RIGHT:
                        self.snakes[c].face_right()
                    elif event.type == CONTROLS.DPAD.DOWN:
                        self.snakes[c].face_down()
                    elif event.type == CONTROLS.DPAD.LEFT:
                        self.snakes[c].face_left()

                    elif event.type == CONTROLS.SELECT:
                        if self.infinite:
                            self.show_game_over(None, False)
                            return

            if time() - self.last_snake_move_time > self.STEP_INTERVAL:
                self.last_snake_move_time = time()

                for screen in self.screens:
                    screen.fill((0, 0, 0))

                    hx, hy = self.snakes[self.screens.index(screen)].head
                    snake_pos = [hx * Snake.PART_SIZE - Snake.PART_SIZE // 2, hy * Snake.PART_SIZE - Snake.PART_SIZE // 2]

                    if snake_pos[0] - Snake.PART_SIZE // 2 - screen.positioning_rect.w // 2 < 0:
                        pg.draw.rect(screen, (255, 0, 0), (0, 0, (snake_pos[0] - Snake.PART_SIZE // 2 - screen.positioning_rect.w // 2) * -1, screen.positioning_rect.h))
                    if snake_pos[0] + Snake.PART_SIZE * 1.5 + screen.positioning_rect.w // 2 > self.PLAYING_FIELD_SIZE:
                        pg.draw.rect(screen, (255, 0, 0), (screen.positioning_rect.w - (snake_pos[0] + Snake.PART_SIZE * 1.5 + screen.positioning_rect.w // 2 - self.PLAYING_FIELD_SIZE), 0, screen.positioning_rect.w, screen.positioning_rect.h))

                    if snake_pos[1] - Snake.PART_SIZE // 2 - screen.positioning_rect.h // 2 < 0:
                        pg.draw.rect(screen, (255, 0, 0), (0, 0, screen.positioning_rect.w, (snake_pos[1] - Snake.PART_SIZE // 2 - screen.positioning_rect.h // 2) * -1))
                    if snake_pos[1] + Snake.PART_SIZE * 1.5 + screen.positioning_rect.h // 2 > self.PLAYING_FIELD_SIZE:
                        pg.draw.rect(screen, (255, 0, 0), (0, screen.positioning_rect.h - (snake_pos[1] + Snake.PART_SIZE * 1.5 + screen.positioning_rect.h // 2 - self.PLAYING_FIELD_SIZE), screen.positioning_rect.w, screen.positioning_rect.h))

                screen_rects = [pg.Rect(snake.head[0] * Snake.PART_SIZE - Snake.PART_SIZE // 2 - self.screens[0].width // 2, snake.head[1] * Snake.PART_SIZE - Snake.PART_SIZE // 2 - self.screens[0].height // 2, self.screens[0].width, self.screens[0].height) for snake in self.snakes[:self.num_screens]]

                alive_snake_count = 0
                alive_player_count = 0
                alive_snake_index = None
                for i, snake in enumerate(self.snakes):
                    if i > self.num_screens - 1:
                        snake.ai_move()

                    snake.move()

                    if snake.dead:
                        if self.infinite:
                            snake.__init__([randint(5, len(self.game_board) - 6), randint(5, len(self.game_board) - 6)],
                                        self.game_board, self.apple_board, snake.og_color, self.apples, snake.is_player, snake.deaths)

                    # Not else or elif because if infinite is on it needs to check again
                    if not snake.dead:
                        alive_snake_index = i 
                        alive_snake_count += 1

                        if i <= self.num_screens - 1:
                            alive_player_count += 1
                    
                    for s, screen in enumerate(self.screens):
                        snake.draw(screen, screen_rects[s])

                if alive_snake_count <= 1 or alive_player_count == 0:
                    self.show_game_over(alive_snake_index, alive_player_count > 0)
                    return

                for apple in self.apples:
                    for s, screen in enumerate(self.screens):
                        apple.draw(screen, screen_rects[s])

                for screen in self.screens:
                    self.display_surf.blit(screen, screen.pos)

                self.draw_splitscreen_lines()
                self.draw_minimap()
            
            #should_quit = self.console_update()
            #if should_quit: return

            pg.display.flip()
