import pygame as pg
import math

from Console.Controllers.controller import Controller, CONTROLS

from time import time

from typing import List

# Define a function to rotate points in 3D
def rotate_3d(point, angle_x, angle_y, angle_z):
    """ Rotates a 3D point around the origin on X, Y, and Z axes """
    x, y, z = point
    
    # Rotate around X-axis
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x
    
    # Rotate around Y-axis
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    
    # Rotate around Z-axis
    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
    
    return x, y, z

# Function to project 3D points to 2D using an isometric view
def project_iso(point, width, height):
    x, y, z = point
    iso_x = x - y
    iso_y = (x + y) * 0.5 - z
    return int(width // 2 + iso_x * 50), int(height // 2 - iso_y * 50)

class Animation:
    def __init__(self, set_property_var: object, start_value: float, end_value: float, anim_time: float, on_finish: object, update_func = lambda: None) -> None:
        self.set_property_var = set_property_var
        self.start_value = start_value
        self.end_value = end_value

        self.start_time = time()
        self.anim_time = anim_time

        self.on_finish = on_finish
        self.update_func = update_func

        self.dist_to_move = self.end_value - self.start_value

    def reset(self) -> None:
        print()
        self.start_time = time()

    def update(self) -> None:
        time_percent = min((time() - self.start_time) / self.anim_time, 1.0)
        self.set_property_var(self.start_value + self.dist_to_move * time_percent)
        self.update_func()

        if time_percent == 1.0: self.on_finish()

class Prism:
    def __init__(self, surface: pg.Surface, x: int, y: int) -> None:
        self.surface = surface

        self.display_width, self.display_height = self.surface.get_size()

        self.x = x
        self.y = y
        self.z = 0

        size = 0.5
        self.vertices = [
            (-size, -size * 2, -size), (size, -size * 2, -size), # Back bottom left, Back bottom right 
            (size, size * 2, -size), (-size, size * 2, -size), # Back top left, Back top right
            (-size, -size * 2, size), (size, -size * 2, size), # Front bottom left, Front bottom right
            (size, size * 2, size), (-size, size * 2, size) # Front top left, front top right
        ]

        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Bottom square
            (4, 5), (5, 6), (6, 7), (7, 4),  # Top square
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]

        self.faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (2, 3, 7, 6),
            (0, 1, 5, 4),
            (0, 2, 6, 4),
            (1, 3, 7, 5)
        ]

        self.angle_x = self.angle_y = self.angle_z = 0

        self.animations = []
        self.last_animation = None

    def set_x_angle(self, angle: float) -> None:
        self.angle_x = angle

    def set_y_angle(self, angle: float) -> None:
        self.angle_y = angle

    def set_z_angle(self, angle: float) -> None:
        self.angle_z = angle

    def queue_left(self) -> None:
        self.animations.append(Animation(self.set_y_angle, self.angle_y, self.angle_y + math.radians(90), 0.5, lambda: self.animations.pop(len(self.animations)-1)))

    def queue_right(self) -> None:
        self.animations.append(Animation(self.set_y_angle, self.angle_y, self.angle_y - math.radians(90), 0.5, lambda: self.animations.pop(len(self.animations)-1)))

    def queue_forward(self) -> None:
        self.animations.append(Animation(self.set_x_angle, self.angle_x, self.angle_x - math.radians(90), 0.5, lambda: self.animations.pop(len(self.animations)-1)))

    def queue_backward(self) -> None:
        self.animations.append(Animation(self.set_x_angle, self.angle_x, self.angle_x + math.radians(90), 0.5, lambda: self.animations.pop(len(self.animations)-1)))

    def draw(self) -> None:
        transformed_vertices = []

        for vx, vy, vz in self.vertices:
            x, y, z = rotate_3d((vx, vy, vz), self.angle_x, self.angle_y, self.angle_z)

            transformed_vertices.append(project_iso((x + self.x, y + self.y - 0.5, z + self.z), self.display_width, self.display_height))

        for face in self.faces:
            pg.draw.polygon(self.surface, (255, 0, 0), [transformed_vertices[face[0]], transformed_vertices[face[1]], transformed_vertices[face[2]], transformed_vertices[face[3]]])

        for edge in self.edges:
            continue
            pg.draw.line(self.surface, (255, 255, 255), transformed_vertices[edge[0]], transformed_vertices[edge[1]], 2)

    def update(self) -> None:
        if len(self.animations) > 0:
            anim = self.animations[0]

            if self.last_animation != anim:
                anim.reset()

            self.last_animation = anim
            anim.update()

class Blocky:
    TILE_WIDTH = 100
    TILE_HEIGHT = 50

    TILE_OFFSET_X = 8
    TILE_OFFSET_Y = 4

    GRID_WIDTH = 10
    GRID_HEIGHT = 10

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers

        self.clock = pg.time.Clock()

        self.SCREEN_WIDTH = self.display_surf.get_width()
        self.SCREEN_HEIGHT = self.display_surf.get_height()

        self.ISO_OFFSET_X = self.SCREEN_WIDTH // 2
        self.ISO_OFFSET_Y = self.SCREEN_HEIGHT // 4

        self.grid = [[0 for x in range(self.GRID_WIDTH)] for y in range(self.GRID_HEIGHT)]

        #self.set_grid_area(1, (3, 3, 4, 4))
        #self.set_grid_area(1, (0, 0, 10, 10))
        self.set_grid_area(1, (3, 0, 4, 4))

        self.tile_surf = pg.Surface((self.TILE_WIDTH, self.TILE_HEIGHT), pg.SRCALPHA)
        pg.draw.polygon(self.tile_surf, (80, 0, 200), [(self.TILE_WIDTH / 2, 0), (self.TILE_WIDTH, self.TILE_HEIGHT / 2), (self.TILE_WIDTH / 2, self.TILE_HEIGHT), (0, self.TILE_HEIGHT / 2)])
        pg.draw.polygon(self.tile_surf, (40, 0, 100), [(self.TILE_WIDTH / 2, self.TILE_OFFSET_Y), (self.TILE_WIDTH - self.TILE_OFFSET_X, self.TILE_HEIGHT / 2), (self.TILE_WIDTH / 2, self.TILE_HEIGHT - self.TILE_OFFSET_Y), (self.TILE_OFFSET_X, self.TILE_HEIGHT / 2)])

        self.prism = Prism(self.display_surf, 5, 1)

        self.main()

    def set_grid_area(self, value: int, area: List[int]) -> None:
        for ay in range(area[3]):
            for ax in range(area[2]):
                x, y = ax + area[0], ay + area[1]

                self.grid[y][x] = value

    def draw_isometric_scene(self) -> None:
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == 0: continue
                self.display_surf.blit(self.tile_surf, (x * self.TILE_WIDTH / 2 - y * self.TILE_WIDTH / 2 + self.ISO_OFFSET_X, x * self.TILE_HEIGHT / 2 + y * self.TILE_HEIGHT / 2 + self.ISO_OFFSET_Y))

    def main(self) -> None:
        while 1:
            dt = self.clock.tick(60)
            self.display_surf.fill((0, 0, 0))

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT: self.prism.queue_left()
                    elif event.key == pg.K_RIGHT: self.prism.queue_right()
                    elif event.key == pg.K_UP: self.prism.queue_forward()
                    elif event.key == pg.K_DOWN: self.prism.queue_backward()

            self.draw_isometric_scene()

            #self.prism.angle_y += 0.005
            self.prism.update()
            self.prism.draw()

            pg.display.flip()