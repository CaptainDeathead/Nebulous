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

class Snither:
    PYGAME_INFO: any = pg.display.Info()
    WIDTH: int = PYGAME_INFO.current_w
    HEIGHT: int = PYGAME_INFO.current_h

    def __init__(self) -> None:
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.FULLSCREEN | pg.DOUBLEBUFF | pg.HWSURFACE)
        self.clock = pg.time.Clock()

        