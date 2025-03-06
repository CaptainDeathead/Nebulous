import pygame as pg

from Console.UI.pygame_gui import Button

from time import time
from random import randint

from typing import Sequence, List, Tuple, Dict

pg.init()

FONTS_PATH = "./Console/UI/Fonts"

class DIRECTION:
    UP    = 0
    RIGHT = 1
    DOWN  = 2
    LEFT  = 3

    @property
    def RANDOM(self) -> int: return randint(0, 3)

class Snake:
    PART_SIZE = 50

    def __init__(self, drawto_surf: pg.Surface, head: Sequence[int], color: pg.Color) -> None:
        self.drawto_surf = drawto_surf

        self.direction = DIRECTION.RANDOM
        self.body = [head]

        self.color = color

        self.grow()

    @property
    def head(self) -> Sequence[int]:
        return self.body[0]

    @property
    def tail(self) -> Sequence[int]:
        return self.body[-1]

    def move(self) -> None:
        for part in self.body:
            match self.direction:
                case DIRECTION.UP:    part = (part[0],     part[1] - 1)
                case DIRECTION.RIGHT: part = (part[0] + 1, part[1])
                case DIRECTION.DOWN:  part = (part[0],     part[1] + 1)
                case DIRECTION.LEFT:  part = (part[0] - 1, part[1])

    def grow(self) -> None:
        match self.direction:
            case DIRECTION.UP:    self.body.append((self.tail[0],     self.tail[1] + 1)) # Push down
            case DIRECTION.RIGHT: self.body.append((self.tail[0] - 1, self.tail[1])) # Push left
            case DIRECTION.DOWN:  self.body.append((self.tail[0],     self.tail[1] - 1)) # Push up
            case DIRECTION.LEFT:  self.body.append((self.tail[0] + 1, self.tail[1])) # Push right

    def draw(self) -> None:
        for part in self.body:
            pg.draw.rect(self.drawto_surf, self.color, (part[0], part[1], self.PART_SIZE, self.PART_SIZE))

    def face_up(self) -> None: self.direction = DIRECTION.UP
    def face_right(self) -> None: self.direction = DIRECTION.RIGHT
    def face_down(self) -> None: self.direction = DIRECTION.DOWN
    def face_left(self) -> None: self.direction = DIRECTION.LEFT

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

        title_lbl = self.fonts["large"].render("Snither", True, (255, 255, 255))
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

class Snither:
    PYGAME_INFO: any = pg.display.Info()
    WIDTH: int = PYGAME_INFO.current_w
    HEIGHT: int = PYGAME_INFO.current_h

    def __init__(self, num_splitscreen_players: int = 1) -> None:
        self.num_screens = num_splitscreen_players

        self.display_surf = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.FULLSCREEN | pg.DOUBLEBUFF | pg.HWSURFACE)
        self.screens = self.setup_screens()
        
        self.clock = pg.time.Clock()

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

    def main(self) -> None:

        while 1:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
            
