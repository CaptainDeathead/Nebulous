import pygame as pg
import random

from Console.Controllers.controller import Controller, CONTROLS

from math import sin, cos, radians
from time import time

from typing import List, Tuple, Sequence

FONTS_PATH = "./UI/Fonts"

SQUARE_SIZE = 48

class LinePiece:
    GRID = [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    CENTER = (1, 1)
    CAN_ROTATE = True

class LOppositePiece:
    GRID = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 1, 1, 0]
    ]

    CENTER = (1, 3)
    CAN_ROTATE = True

class LPiece:
    GRID = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 1, 1, 1]
    ]

    CENTER = (2, 3)
    CAN_ROTATE = True

class SquarePiece:
    GRID = [
        [1, 1, 0, 0],
        [1, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    CENTER = (0, 0)
    CAN_ROTATE = False

class RStaircasePiece:
    GRID = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 1, 1],
        [0, 1, 1, 0]
    ]

    CENTER = (2, 3)
    CAN_ROTATE = True

class LStaircasePiece:
    GRID = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 1, 0]
    ]

    CENTER = (1, 3)
    CAN_ROTATE = True

class TPiece:
    GRID = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [1, 1, 1, 0]
    ]

    CENTER = (1, 3)
    CAN_ROTATE = True

class Piece:
    def __init__(self, piece_type: LinePiece | LOppositePiece | LPiece | SquarePiece | RStaircasePiece | LStaircasePiece | TPiece, x: int, y: int, color: Tuple[int]) -> None:
        self.piece_type = piece_type
        self.x = x
        self.y = y
        self.color = color
        self.rotation = 0

        self.rotated_points = self.piece_type.GRID.copy()
        self.next_rotate()

    def rotate_points_around_center(self, points: List[List[int]], center: Sequence[int], rotation: int) -> List[Sequence[int]]:
        new_points = []
        angle = radians(rotation)

        for y in range(len(points)):
            for x in range(len(points[y])):
                if points[y][x] == 0: continue

                qx = center[0] + cos(angle) * (x - center[0]) - sin(angle) * (y - center[1])
                qy = center[1] + sin(angle) * (x - center[0]) + cos(angle) * (y - center[1])

                new_points.append((int(round(qx, 0)), int(round(qy, 0))))
                
        return new_points

    def next_rotate(self) -> None:
        if not self.piece_type.CAN_ROTATE:
            self.flat_rotated_points = []

            for y in range(len(self.rotated_points)):
                for x in range(len(self.rotated_points[y])):
                    if self.rotated_points[y][x] == 0: continue

                    self.flat_rotated_points.append((x, y))

            return

        self.rotation = (self.rotation + 90) % 360
        self.flat_rotated_points = self.rotate_points_around_center(self.rotated_points, self.piece_type.CENTER, self.rotation)

    def draw(self, screen: pg.Surface) -> None:
        for x, y in self.flat_rotated_points:
            pg.draw.rect(screen, self.color, (x * SQUARE_SIZE + self.x * SQUARE_SIZE, y * SQUARE_SIZE + self.y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

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

class Game:
    ALL_PIECE_TYPES = (LinePiece, LOppositePiece, LPiece, SquarePiece, RStaircasePiece, LStaircasePiece, TPiece)
    DEFAULT_SOFT_DROP_TIME = 0.2

    VALID_PIECE_COLORS = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255))

    def __init__(self, screen: Screen, controller: Controller, num_rows: int, num_cols: int, high_score: int = 0, just_reset: bool = False) -> None:
        self.screen = screen
        self.controller = controller

        self.num_rows = num_rows
        self.num_cols = num_cols

        self.BASE_SCORES = [40, 100, 300, 1200]

        self.level = 1
        self.score = 0
        self.high_score = high_score

        self.active_piece = self.new_piece()
        self.spring_piece_back()

        self.last_fall_time = time()
        self.soft_drop_time = self.DEFAULT_SOFT_DROP_TIME
        self.last_soft_drop_time = time()

        self.grid = [[0 for x in range(self.num_cols)] for y in range(self.num_rows)]
        self.color_grid = [[(0, 0, 0) for x in range(self.num_cols)] for y in range(self.num_rows)]

        self.score_surface = pg.Surface((self.screen.width, self.screen.height - self.num_rows * SQUARE_SIZE))
        self.score_surface_pos = (0, self.screen.height - self.score_surface.height)

        self.score_font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", 24)

        self.lines_cleared_since_level = 0

        self.next_piece = self.new_piece()

        self.just_reset = just_reset

    def show_game_over(self) -> None:
        self.__init__(self.screen, self.controller, self.num_rows, self.num_cols, self.high_score, True)

    def new_piece(self) -> Piece:
        piece_type = random.choice(self.ALL_PIECE_TYPES)
        piece = Piece(piece_type, self.num_cols // 2 - piece_type.CENTER[0], -piece_type.CENTER[1], random.choice(self.VALID_PIECE_COLORS))

        return piece

    def check_adjacent_blocks(self) -> Sequence[bool]:
        left_block = False
        right_block = False

        for px, py in self.active_piece.flat_rotated_points:
            x = self.active_piece.x + px
            y = self.active_piece.y + py

            if x - 1 < 0:
                left_block = True
            else:
                if self.grid[y][x - 1] == 1:
                    left_block = True

            if x + 1 >= self.num_cols:
                right_block = True
            else:
                if self.grid[y][x + 1] == 1:
                    right_block = True

        return (left_block, right_block)

    def check_piece_active(self, piece: Piece) -> bool:
        for px, py in piece.flat_rotated_points:
            if piece.y + py == self.num_rows - 1: return True

            if self.grid[piece.y + py + 1][piece.x + px] != 0: return True

        return False

    def spring_piece_back(self) -> None:
        max_move_x = 0

        for px, py in self.active_piece.flat_rotated_points:
            if px + self.active_piece.x < 0:
                move_x = (px + self.active_piece.x) * -1
                if move_x > max_move_x:
                    max_move_x = move_x

            elif px + self.active_piece.x >= self.num_cols:
                move_x = px + self.active_piece.x - self.num_cols - 1
                if move_x < max_move_x:
                    max_move_x = move_x

        self.active_piece.x += max_move_x

    def move_piece_left(self) -> None:
        if not self.check_adjacent_blocks()[0]:
            self.active_piece.x -= 1

    def move_piece_right(self) -> None:
        if not self.check_adjacent_blocks()[1]:
            self.active_piece.x += 1
            
    def solidify_piece(self, piece: Piece) -> None:
        for px, py in piece.flat_rotated_points:
            if self.grid[piece.y + py][piece.x + px] == 0:
                self.grid[piece.y + py][piece.x + px] = 1
                self.color_grid[piece.y + py][piece.x + px] = piece.color

    def draw_grid(self) -> None:
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] != 0:
                    pg.draw.rect(self.screen, self.color_grid[y][x], (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def clear_row(self, row_index: int) -> None:
        self.grid.pop(row_index)
        self.grid.insert(0, [0 for i in range(self.num_cols)])

        self.color_grid.pop(row_index)
        self.color_grid.insert(0, [(0, 0, 0) for i in range(self.num_cols)])

    def scan_rows(self) -> None:
        rows_to_clear = []

        for y in range(0, self.num_rows):
            if y == 0: continue

            row_full = True

            for x in range(self.num_cols):
                if self.grid[y][x] == 0:
                    row_full = False
                    break

            if row_full:
                rows_to_clear.append(y)

        if len(rows_to_clear) > 0:
            if len(rows_to_clear) <= len(self.BASE_SCORES):
                points = self.BASE_SCORES[len(rows_to_clear) - 1] * (self.level)
            else:
                points = self.BASE_SCORES[-1] * (self.level)

            self.score += points
            self.high_score = max(self.high_score, self.score)

        for row in rows_to_clear:
            self.clear_row(row)
            self.lines_cleared_since_level += 1

        # Level up happens after score
        if self.lines_cleared_since_level >= 10:
            self.level += 1
            self.lines_cleared_since_level = 0

    def move_piece_down(self) -> None:
        if self.check_piece_active(self.active_piece):
            if self.active_piece.y < 0:
                self.show_game_over()
                return

            self.solidify_piece(self.active_piece)
            self.active_piece = self.next_piece
            self.next_piece = self.new_piece()
            self.spring_piece_back()

        else:
            self.active_piece.y += 1
            self.last_fall_time = time()
            self.scan_rows()

    def check_piece_collision(self) -> bool:
        for px, py in self.active_piece.flat_rotated_points:
            x = self.active_piece.x + px
            y = self.active_piece.y + py

            if self.grid[y][x] != 0: return True

        return False

    def rotate_piece(self) -> None:
        old_x, old_y = self.active_piece.x, self.active_piece.y
        self.active_piece.next_rotate()
        self.spring_piece_back()

        if self.check_piece_collision():
            self.active_piece.x = old_x
            self.active_piece.y = old_y
            for i in range(3): self.active_piece.next_rotate()

    def soft_drop(self) -> None:
        if time() - self.last_soft_drop_time >= self.soft_drop_time:
            self.move_piece_down()
            self.last_soft_drop_time = time()
            self.soft_drop_time *= (1 / (self.soft_drop_time+1)**2)

    def reset_soft_drop(self) -> None:
        self.soft_drop_time = self.DEFAULT_SOFT_DROP_TIME

    def draw_score_screen(self) -> None:
        self.score_surface.fill((100, 100, 100))

        lvl_lbl = self.score_font.render(f"Level: {self.level}", True, (255, 255, 255))
        score_lbl = self.score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        high_score_lbl = self.score_font.render(f"High: {self.high_score}", True, (255, 255, 255))
        next_lbl = self.score_font.render("Next:", True, (255, 255, 255))

        self.score_surface.blit(lvl_lbl, (10, 20))
        self.score_surface.blit(score_lbl, (10, 52))
        self.score_surface.blit(high_score_lbl, (10, 85))
        self.score_surface.blit(next_lbl, (240, 20))

        size = 20

        pg.draw.rect(self.score_surface, (0, 0, 0), (370, 10, 5 * size, 5 * size))
        for y in range(4):
            for x in range(4):
                if self.next_piece.piece_type.GRID[y][x] == 0: continue
                pg.draw.rect(self.score_surface, self.next_piece.color, (370 + x * size, 10 + y * size, size, size))

        self.screen.blit(self.score_surface, self.score_surface_pos)

    def update(self, dt: float) -> None:
        self.screen.fill((0, 0, 0))

        self.just_reset = False

        soft_drop_pressed = False

        for event in self.controller.event.get():
            if event.type == CONTROLS.DPAD.LEFT:
                self.move_piece_left()
            elif event.type == CONTROLS.DPAD.RIGHT:
                self.move_piece_right()

            elif event.type == CONTROLS.ABXY.A:
                self.rotate_piece()
            elif event.type == CONTROLS.ABXY.B:
                self.soft_drop()
                soft_drop_pressed = True
            
        if not soft_drop_pressed:
            self.reset_soft_drop()

        if time() - self.last_fall_time >= 0.5:
            self.move_piece_down()

        self.draw_grid()
        self.active_piece.draw(self.screen)

        self.draw_score_screen()

class Tetris:
    NUM_ROWS = 20
    NUM_COLS = 10
    GAME_MULTIPLIER = SQUARE_SIZE

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.get_num_players = lambda: 4
        self.controllers = controllers

        self.clock = pg.time.Clock()

        self.screens = [Screen(pg.Rect(x*self.NUM_COLS * self.GAME_MULTIPLIER, 0, self.NUM_COLS * self.GAME_MULTIPLIER, self.display_surf.height)) for x in range(self.get_num_players())]
        self.games = [Game(self.screens[i], self.controllers[i], self.NUM_ROWS, self.NUM_COLS) for i in range(self.get_num_players())]

        self.main()

    def draw_lines(self) -> None:
        for screen in self.screens:
            pg.draw.line(self.display_surf, (255, 255, 255), (screen.x + screen.width + 2, 0), (screen.x + screen.width + 2, screen.height), 5)
            pg.draw.line(self.display_surf, (255, 255, 255), (screen.x + screen.width + 2, 0), (screen.x + screen.width + 2, screen.height), 5)

    def main(self) -> None:
        while 1:
            dt = self.clock.tick(60)
            self.display_surf.fill((90, 90, 90))

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.games[1].rotate_piece()
                        #self.games[0].active_piece.next_rotate()
                    elif event.key == pg.K_LEFT:
                        self.games[1].move_piece_left()
                    elif event.key == pg.K_RIGHT:
                        self.games[1].move_piece_right()

                    elif event.key == pg.K_w:
                        self.games[0].rotate_piece()
                    elif event.key == pg.K_a:
                        self.games[0].move_piece_left()
                    elif event.key == pg.K_d:
                        self.games[0].move_piece_right()

                    elif event.key == pg.K_y:
                        self.games[2].rotate_piece()
                    elif event.key == pg.K_g:
                        self.games[2].move_piece_left()
                    elif event.key == pg.K_j:
                        self.games[2].move_piece_right()

            keys = pg.key.get_pressed()

            if keys[pg.K_DOWN]:
                self.games[1].soft_drop()
            else:
                self.games[1].reset_soft_drop()

            if keys[pg.K_s]:
                self.games[0].soft_drop()
            else:
                self.games[0].reset_soft_drop()

            if keys[pg.K_h]:
                self.games[2].soft_drop()
            else:
                self.games[2].reset_soft_drop()

            self.console_update()

            for i, game in enumerate(self.games):
                if i < self.get_num_players():
                    game.update(dt)
                else:
                    if not game.just_reset:
                        game.show_game_over()

                self.display_surf.blit(game.screen, (game.screen.x, game.screen.y))

            self.draw_lines()

            pg.display.flip()
