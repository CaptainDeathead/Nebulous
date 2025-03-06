import pygame as pg

from time import time
from random import randint

from typing import Sequence, List, Tuple, Dict

pg.init()

class DIRECTION:
    UP    = 0
    RIGHT = 1
    DOWN  = 2
    LEFT  = 3

    @property
    def RANDOM(self) -> int: return randint(0, 3)

class Snake:
    PART_SIZE = 50

    def __init__(self, drawto_surf: pg.Surface, head: Sequence[int]) -> None:
        self.drawto_surf = drawto_surf

        self.direction = DIRECTION.RANDOM
        self.body = [head]

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