import pygame as pg

from Console.Controllers.controller import Controller, CONTROLS
from Console.sound import generate_sine_wave

from time import time
from json import loads
from math import dist, sin, cos, atan2, pi, sqrt
from ast import literal_eval
from random import randint, choice, uniform
from shapely import box, Polygon

from typing import List, Sequence, Dict

FONTS_PATH = "./UI/Fonts"

class Poison:
    def __init__(self, parent: any, deal_damage_func: object, on_poison_end: object, damage: int, duration: int, lifesteal: float) -> None:
        self.parent = parent
        self.deal_damage_func = deal_damage_func
        self.on_poison_end = on_poison_end

        self.damage = damage
        self.duration = duration
        self.lifesteal = lifesteal

        self.last_tick_time = time()

    def update(self) -> None:
        if time() - self.last_tick_time >= 1:
            self.duration -= time() - self.last_tick_time
            self.last_tick_time = time()

            self.deal_damage_func(self.damage)
            self.parent.give_lifesteal(self.damage * self.lifesteal)

            if self.duration <= 0: self.on_poison_end(self)

class Bullet:
    def __init__(self, parent: any, x: float, y: float, velocity: List[float], base_damage: int, damage_growth: float,
                 poison_damage: int, penetration: float, lifesteal: float, bullet_img: pg.Surface) -> None:

        self.parent = parent
        
        self.start_x = x
        self.start_y = y

        self.x = x
        self.y = y
        self.velocity = velocity

        self.base_damage = base_damage
        self.damage_growth = damage_growth
        self.poison_damage = poison_damage
        self.penetration = penetration
        self.lifesteal = lifesteal

        self.image = bullet_img

    @property
    def distance_travelled(self) -> float:
        return dist((self.x, self.y), (self.start_x, self.start_y))

    def move(self, dt: float) -> None:
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

    def draw(self, screen: pg.Surface, draw_parent: any) -> None:
        screen_rect = pg.Rect(draw_parent.x - screen.width // 2 + self.image.width // 2, draw_parent.y - screen.height // 2 + self.image.height // 2, screen.width, screen.height)

        if not pg.Rect(self.x - self.image.width // 2, self.y - self.image.height // 2, self.image.width, self.image.height).colliderect(screen_rect): return

        screen.blit(self.image, (self.x - self.image.width // 2 - screen_rect.x, self.y - self.image.height // 2 - screen_rect.y))

    def hit(self, target: any) -> None:
        health_damage = self.base_damage * (self.damage_growth * self.distance_travelled)
        shield_damage = health_damage * self.penetration

        target.take_damage(health_damage)
        target.take_shield_damage(shield_damage)

        if self.poison_damage > 0:
            target.add_poison(self.parent, self.poison_damage, (self.lifesteal - 1))

        self.parent.give_lifesteal(health_damage * (self.lifesteal - 1))

class Powerup:
    WIDTH = 50
    HEIGHT = 50

    def __init__(self, x: int, y: int, rarity: str, powerup_info: Dict[str, Dict], on_pickup: object) -> None:
        self.x = x
        self.y = y

        self.rarity = rarity
        self.name = choice(list(powerup_info[rarity]["types"]))
        self.powerup_info = powerup_info
        self.info = self.powerup_info[rarity]["types"][self.name]

        self.on_pickup = on_pickup

        self.color = literal_eval(self.powerup_info[rarity]["color"])

        self.blurb = self.info["blurb"]
        self.description = self.info["description"]
        self.effect = self.info["effect"]
        self.value = self.info["value"]

        self.image = pg.Surface((self.WIDTH, self.HEIGHT), pg.SRCALPHA)
        pg.draw.aacircle(self.image, self.color, (self.WIDTH // 2, self.HEIGHT // 2), self.WIDTH // 2)

    def render_popup(self) -> pg.Surface:
        title_font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", size=40)
        blurb_font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", size=20)
        description_font = pg.font.Font(f"{FONTS_PATH}/PressStart2P.ttf", size=20)

        rect_w, rect_h = 600, 400
        surface = pg.Surface((rect_w, rect_h), pg.SRCALPHA)

        pg.draw.rect(surface, self.color, (0, 0, rect_w, rect_h), border_radius=20)

        curr_y = 20
        title_lbl = title_font.render(self.name, True, (255, 255, 255))
        surface.blit(title_lbl, (rect_w // 2 - title_lbl.width // 2, curr_y))
        curr_y += title_lbl.height + 20

        blurb_lbl = blurb_font.render(f'"{self.blurb}"', True, (255, 255, 255))
        surface.blit(blurb_lbl, (rect_w // 2 - blurb_lbl.width // 2, curr_y))
        curr_y += blurb_lbl.height

        description_lbl = description_font.render(self.description, True, (255, 255, 255))
        rarity_lbl = blurb_font.render(self.rarity, True, (255, 255, 255))

        rarity_y = rect_h - rarity_lbl.height - 20
        surface.blit(rarity_lbl, (rect_w // 2 - rarity_lbl.width // 2, curr_y))

        description_y = rect_h + (rarity_y - curr_y) // 2 - description_lbl.height // 2
        surface.blit(description_lbl, (rect_w // 2 - description_lbl.width // 2, description_y))

        return surface

    def draw(self, screen: pg.Surface, draw_parent: any) -> None:
        screen_rect = pg.Rect(draw_parent.x - screen.width // 2 + self.image.width // 2, draw_parent.y - screen.height // 2 + self.image.height // 2, screen.width, screen.height)

        if not pg.Rect(self.x - self.image.width // 2, self.y - self.image.height // 2, self.image.width, self.image.height).colliderect(screen_rect): return

        screen.blit(self.image, (self.x - self.image.width // 2 - screen_rect.x, self.y - self.image.height // 2 - screen_rect.y))

    def pickup(self, player: any) -> None:
        player.parse_effect(self.effect, self.value)
        player.show_powerup_popup(self.render_popup())

        self.on_pickup(self)

class Shape:
    POISON_DURATION = 10

    def __init__(self, x: float, y: float, shape_name: str, shape_info: Dict[str, Dict], shape_image: pg.Surface, enemy_shape_image: pg.Surface, bullets: List[Bullet],
                 bullet_img: pg.Surface, is_player: bool, controller: Controller | None = None, squad: List[any] = []) -> None:

        self.x = x
        self.y = y
        self.rotation = 0

        self.shape_name = shape_name
        self.shape_info = shape_info
        self.info = self.shape_info[self.shape_name]

        self.shape_image = shape_image
        self.enemy_shape_image = enemy_shape_image
        self.rotated_shape_image = shape_image.copy()
        self.rotated_enemy_shape_image = enemy_shape_image.copy()

        self.bullet_img = bullet_img

        self.is_player = is_player
        self.controller = controller
        self.squad = squad

        self.max_hp = self.info['hp'] # literal
        self.max_shield = self.info['shield'] # literal
        self.max_speed = self.info['speed'] # literal
        self.damage = self.info['damage'] # literal
        self.firerate = self.info['firerate'] # literal 
        self.bullet_speed = self.info['bullet_speed'] # literal
        self.penetration = self.info['penetration'] # percent
        self.shield_regen_rate = self.info['shield_regen'] # literal
        self.lifesteal = 1.0 # percent
        self.poison_damage = 0 # literal
        self.zone_resistance = 1.0 # percent
        self.health_regen_rate = self.info["health_regen"] # literal
        self.damage_growth = 1.0 # percent

        self.hp = self.max_hp
        self.shield = self.max_shield

        self.last_shoot_time = 0

        self.bullets = bullets
        self.poisons = []

        self.showing_powerup_popup = False
        self.powerup_popup = None

        self.rect = pg.Rect(0, 0, self.shape_image.width, self.shape_image.height)

    def change_var_value(self, var: object, value_type: str, value: any) -> None:
        if value_type == 'percentage_increase':
            var *= value

        elif value_type == 'increase':
            var += value

    def parse_effect(self, effect: str, value: any) -> None:
        """Target.Effect.Valuetype, value"""

        args = effect.split('.')

        if len(args) < 3:
            raise Exception("Provided args is not valid! 'arg1.arg2.arg3' is required!")

        if args[0] == 'player':
            var = None

            match args[1]:
                case 'maxhp': var = self.max_hp
                case 'shield': var = self.max_shield
                case 'speed': var = self.max_speed
                case 'damage': var = self.damage
                case 'firerate': var = self.firerate
                case 'bulletspeed': var = self.bullet_speed
                case 'penetration': var = self.penetration
                case 'shieldregenrate': var = self.shield_regen_rate
                case 'lifesteal': var = self.lifesteal
                case 'poisondamage': var = self.poison_damage
                case 'zoneresistance': var = self.zone_resistance
                case 'healthregenrate': var = self.health_regen_rate
                case 'damagegrowth': var = self.damage_growth

            self.change_var_value(var, args[2], value)

    def show_powerup_popup(self, powerup_popup: pg.Surface) -> None:
        self.powerup_popup = powerup_popup
        self.showing_powerup_popup = True

    def take_damage(self, damage: float) -> None:
        self.hp -= damage

        if self.hp <= 0:
            self.die()

    def take_shield_damage(self, shield_damage: float) -> None:
        leftover_shield_damage = shield_damage - self.shield

        if leftover_shield_damage > 0:
            self.take_damage(leftover_shield_damage)
            self.shield = 0
        else:
            self.shield -= shield_damage

    def on_poison_end(self, poison: Poison) -> None:
        self.poisons.remove(poison)

    def add_poison(self, poison_damage: int, poison_lifesteal: float) -> None:
        self.poisons.append(Poison(self.take_damage, self.on_poison_end, poison_damage, self.POISON_DURATION, poison_lifesteal))

    def give_lifesteal(self, lifesteal_health: float) -> None:
        self.hp = min(self.max_hp, self.hp + lifesteal_health)

    def move_up(self, dt: float) -> None:
        self.y -= self.max_speed * dt * 30
        self.rotation = 0

    def move_right(self, dt: float) -> None:
        self.x += self.max_speed * dt * 30
        self.rotation = 270

    def move_down(self, dt: float) -> None:
        self.y += self.max_speed * dt * 30
        self.rotation = 180

    def move_left(self, dt: float) -> None:
        self.x -= self.max_speed * dt * 30
        self.rotation = 90

    def shoot(self) -> None:
        if time() - self.last_shoot_time >= 1 / self.firerate:
            self.last_shoot_time = time()

            match self.rotation:
                case 0: bullet_vel = [0, -self.max_speed * (self.bullet_speed + 1)]
                case 90: bullet_vel = [-self.max_speed * (self.bullet_speed + 1), 0]
                case 180: bullet_vel = [0, self.max_speed * (self.bullet_speed + 1)]
                case 270: bullet_vel = [self.max_speed * (self.bullet_speed + 1), 0]
            #else: 
            #    bullet_vel = [self.x * (self.bullet_speed + 1), self.y * (self.bullet_speed + 1)]

            self.bullets.append(Bullet(self, self.x, self.y, bullet_vel, self.damage, self.damage_growth, self.poison_damage, self.penetration, self.lifesteal, self.bullet_img))

    def ai_move(self) -> None:
        ...

    def update(self, dt: float) -> None:
        for poison in self.poisons:
            poison.update()

        if self.is_player:
            for event in self.controller.event.get():
                if event.type == CONTROLS.DPAD.UP: self.move_up(dt)
                elif event.type == CONTROLS.DPAD.RIGHT: self.move_right(dt)
                elif event.type == CONTROLS.DPAD.DOWN: self.move_down(dt)
                elif event.type == CONTROLS.DPAD.LEFT: self.move_left(dt)

                elif event.type == CONTROLS.ABXY.B: self.shoot()
                elif event.type == CONTROLS.ABXY.A:
                    if self.showing_powerup_popup:
                        self.showing_powerup_popup = False
        else:
            self.ai_move()

        self.rotated_shape_image = pg.transform.rotate(self.shape_image, self.rotation)
        self.rotated_enemy_shape_image = pg.transform.rotate(self.enemy_shape_image, self.rotation)

    def draw(self, screen: pg.Surface, draw_parent: any) -> None:
        if draw_parent in self.squad:
            image = self.rotated_shape_image
        else:
            image = self.rotated_enemy_shape_image

        screen_rect = pg.Rect(draw_parent.x - screen.width // 2 + image.width // 2, draw_parent.y - screen.height // 2 + image.height // 2, screen.width, screen.height)

        if not pg.Rect(self.x, self.y, image.width, image.height).colliderect(screen_rect): return

        screen.blit(image, (self.x - screen_rect.x, self.y - screen_rect.y))

        if self.showing_powerup_popup and draw_parent is self:
            screen.blit(self.powerup_popup, (screen.width // 2 - self.powerup_popup.width // 2, screen.height // 2 - self.powerup_popup.height // 2))

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

        self.shape_index = 0

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

class Safezone:
    NUM_POINTS = 100
    DISTANCE_TO_MOVE_REDUCTION = 1000
    TARGET_RADIUS_ALLOWANCE = 1.05
    SCALING = 80

    def __init__(self, map_size_x: int, map_size_y: int, phase_config: Dict[int, Dict]) -> None:
        self.map_size_x = map_size_x
        self.map_size_y = map_size_y

        self.phase_config = phase_config
        self.phase_index = 0
        self.start_radius = self.phase_config[self.phase_index]["radius"]

        self.color = pg.Color(255, 0, 0)

        self.scaled_width = map_size_x // self.SCALING
        self.scaled_height = map_size_y // self.SCALING

        self.polygon = self.generate_circle_polygon(self.start_radius, (self.map_size_x / 2, self.map_size_y / 2), self.NUM_POINTS)
        self.surface = pg.Surface((self.scaled_width, self.scaled_height))
        
        self.next_phase()

    def generate_circle_polygon(self, radius: float, center: Sequence[float], num_points: int) -> List[Sequence[float]]:
        points = []

        for i in range(num_points):
            angle = 2 * pi * i / num_points

            x = center[0] + radius * cos(angle)
            y = center[1] + radius * sin(angle)

            points.append((x, y))

        return points

    def next_phase(self) -> None:
        if self.phase_index >= len(self.phase_config) - 1:
            self.target_radius = 0
            self.distances_to_move = self.calculate_distances()
            return

        self.phase_index += 1

        self.target = self.phase_config[self.phase_index]["target"]
        self.target_radius = self.phase_config[self.phase_index]["radius"]
        self.zone_speed = 0.001
        self.distances_to_move = self.calculate_distances()

    def calculate_distances(self) -> List[float]:
        distances = []

        for point in self.polygon:
            distance_to_move = dist(point, self.target) - self.target_radius
            distances.append(distance_to_move)

        return distances

    def shrink(self, dt: float) -> None:
        new_polygon = []
        radius_sum = 0

        for p, point in enumerate(self.polygon):
            angle_to_target = atan2(point[1] - self.target[1], point[0] - self.target[0])
            curr_distance_to_move = dist(point, self.target) - self.target_radius

            new_point = (point[0] - cos(angle_to_target) * self.distances_to_move[p] * dt * self.zone_speed, point[1] - sin(angle_to_target) * self.distances_to_move[p] * dt * self.zone_speed)
            new_polygon.append(new_point)

            radius_sum += curr_distance_to_move

        avg_radius = radius_sum / len(self.polygon)
        if avg_radius < 200:
            self.next_phase()

        self.polygon = new_polygon

    def update(self, dt: float) -> None:
        self.shrink(dt)

    def draw(self) -> None:
        screen_verts = [(px//100, py//100) for px, py in self.polygon]

        self.surface.fill((255, 0, 0))
        pg.draw.polygon(self.surface, (0, 0, 0), screen_verts)
        #pg.image.save(self.surface, 'e.png')

    def blit(self, screen: pg.Surface, draw_parent: Shape) -> None:
        x = max(min((draw_parent.x - screen.width / 2) / 100, self.surface.width), 0)
        y = max(min((draw_parent.y - screen.height / 2) / 100, self.surface.height), 0)
        #width = max(min(x + screen.width / 100, self.surface.height), 0)
        #height = max(min(y + screen.height / 100, self.surface.height), 0)
        width = screen.width / self.SCALING * 1.5
        height = screen.height / self.SCALING * 1.5

        #print(x, y, width, height)

        crop_area = pg.Rect(x, y, width, height)
        cropped_surf = pg.transform.scale_by(self.surface.subsurface(crop_area), self.SCALING)

        screen.fill((255, 255, 255))
        screen.blit(cropped_surf, (0, 0))

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

        self.title_lbl = self.fonts["large"].render("Shape Royale", True, (255, 255, 255))

        self.info_lbl = self.fonts["medium"].render   ("Press A to ready / unready...", True, (255, 255, 255))
        self.info_lbl.blit(self.fonts["medium"].render("      A", True, (0, 255, 0)))

        self.timer_active = False
        self.timer_start_time = time()
        self.start_game = False
        self.last_timer_time = 0
        self.timer_first_beep = True

        self.timer_start_lbl = self.fonts["medium"].render("Game starting in  ...", True, (255, 255, 255))
        self.timer_end_lbls = [self.fonts["medium"].render(f"                 {i}", True, (0, 0, 255)) for i in range(1, self.TIMER_LENGTH + 1)]

        self.shape_images = [
            pg.image.load("../Games/ShapeRoyale/Data/assets/Square_Sprite_Player.png").convert_alpha(),
            pg.image.load("../Games/ShapeRoyale/Data/assets/Triangle_Sprite_Player.png").convert_alpha(),
            pg.image.load("../Games/ShapeRoyale/Data/assets/Circle_Sprite_Player.png").convert_alpha()
        ]

        self.shape_names = ("Square", "Triangle", "Circle")

        with open("../Games/ShapeRoyale/Data/shapes.json", "r") as f:
            self.shape_info = loads(f.read())

        self.players[0].controller.plugged_in = True
        self.players[1].controller.plugged_in = True
        self.players[1].ready = True
        self.players[2].controller.plugged_in = True
        self.players[2].ready = True
        self.players[3].controller.plugged_in = True
        self.players[3].ready = True

        self.main()

    def reset_timer(self) -> None:
        self.timer_active = False
        self.timer_start_time = time()
        self.timer_first_beep = True

    def check_game_start(self) -> None:
        for player in self.players:
            if player.controller.plugged_in and not player.ready:
                self.reset_timer()
                return
            
            timer_time = self.TIMER_LENGTH - (time() - self.timer_start_time)
            self.timer_active = True

            if timer_time <= 1:
                self.start_game = True

    def draw_player_cards(self) -> None:
        card_w = 350
        card_h = 500
        pad_w = 50

        cards_w = card_w * 4 + pad_w * 3
        start_x = self.width // 2 - cards_w // 2

        card_y = 350

        ready_line_w = 120

        for i, player in enumerate(self.players):
            x = start_x + (card_w + pad_w) * i

            name_lbl = self.fonts["medium"].render(f"Player {i + 1}", True, (255, 255, 255))
            self.display_surf.blit(name_lbl, (x + card_w // 2 - name_lbl.width // 2, card_y - 70))

            pg.draw.line(self.display_surf, player.ready_color, (x + card_w // 2 - ready_line_w // 2, card_y - 20), (x + card_w // 2 + ready_line_w // 2, card_y - 20), 5)

            player_rect = pg.Rect(x, card_y, card_w, card_h)
            pg.draw.rect(self.display_surf, (150, 150, 150), player_rect, border_radius = 20)

            if not player.controller.plugged_in:
                pg.draw.line(self.display_surf, (255, 0, 0), (x + 20, card_y + 20), (x + card_w - 20, card_y + card_h - 20), 5)
                pg.draw.line(self.display_surf, (255, 0, 0), (x + card_w - 20, card_y + 20), (x + 20, card_y + card_h - 20), 5)
                continue
            
            selected_shape = self.shape_names[player.shape_index]
            shape_name_lbl = self.fonts["small"].render(f"Shape: {selected_shape}", True, (255, 255, 255))
            shape_class_lbl = self.fonts["small"].render(f"Class: {self.shape_info[selected_shape]['class']}", True, (255, 255, 255))

            curr_y = card_y + 20

            self.display_surf.blit(shape_name_lbl, (x + card_w // 2 - shape_name_lbl.width // 2, curr_y))
            curr_y += shape_name_lbl.height + 5

            self.display_surf.blit(shape_class_lbl, (x + card_w // 2 - shape_class_lbl.width // 2, curr_y))
            curr_y += shape_class_lbl.height + 20

            shape_image = pg.transform.smoothscale_by(self.shape_images[player.shape_index], 0.2)
            self.display_surf.blit(shape_image, (x + card_w // 2 - shape_image.width // 2, curr_y))
            curr_y += shape_image.height + 20

            shape_hp = self.shape_info[selected_shape]["hp"]
            shape_firerate = self.shape_info[selected_shape]["firerate"]
            shape_dmg = self.shape_info[selected_shape]["damage"]
            shape_speed = self.shape_info[selected_shape]["speed"]

            shape_info_lbls = [
                self.fonts["small"].render(f"Health: {shape_hp}HP", True, (255, 255, 255)),
                self.fonts["small"].render(f"Rate of fire: {shape_firerate}/s", True, (255, 255, 255)),
                self.fonts["small"].render(f"Damage: {shape_dmg}HP", True, (255, 255, 255)),
                self.fonts["small"].render(f"Speed: {shape_speed}u/s", True, (255, 255, 255)),
            ]

            largest_width = shape_info_lbls[1].width

            for shape_info_lbl in shape_info_lbls:
                self.display_surf.blit(shape_info_lbl, (x + card_w // 2 - largest_width // 2, curr_y))
                curr_y += shape_info_lbl.height + 5

    def main(self) -> None:
        while not self.start_game:
            self.display_surf.fill((0, 0, 0))
            self.clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.players[0].ready = not self.players[0].ready

            for i, controller in enumerate(self.controllers):
                for event in controller.event.get():
                    if event.type == CONTROLS.ABXY.A:
                        self.players[i].ready = not self.players[i].ready

            self.draw_player_cards()

            self.display_surf.blit(self.title_lbl, (self.width // 2 - self.title_lbl.width // 2, 100))

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

            self.console_update()

            pg.display.flip()

class ShapeRoyale:
    PYGAME_INFO: any = pg.display.Info()
    WIDTH: int = PYGAME_INFO.current_w
    HEIGHT: int = PYGAME_INFO.current_h

    MAP_SIZE = 100_000
    MAP_SIZE_X = MAP_SIZE
    MAP_SIZE_Y = MAP_SIZE

    NUM_PHASES = 4
    NUM_PLAYERS = 100
    NUM_POWERUPS = 2400 # this must be divisible by the NUM_POWERUP_SECTIONS below
    NUM_POWERUP_SECTIONS = 12
    POWERUP_SECTION_SIZE = int(NUM_POWERUPS / NUM_POWERUP_SECTIONS)

    MAX_BULLET_TRAVEL_DIST = 2000

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        if not (self.NUM_POWERUPS / self.NUM_POWERUP_SECTIONS).is_integer() or self.NUM_POWERUPS % self.NUM_POWERUP_SECTIONS != 0:
            raise Exception("NUM_POWERUPS must be divisible by NUM_POWERUP_SECTIONS such that the resualt is a valid integer!")

        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers

        self.main_menu = MainMenu(self.display_surf, self.console_update, self.controllers)

        self.num_screens = self.get_num_players()

        self.screens = self.setup_screens()
        self.clock = pg.time.Clock()

        self.bullet_img = pg.transform.smoothscale(pg.image.load("../Games/ShapeRoyale/Data/assets/Bullet_Sprite.png").convert_alpha(), (10, 10))

        self.generate_safezone_phases(self.NUM_PHASES)
        self.safezone = Safezone(self.MAP_SIZE_X, self.MAP_SIZE_Y, self.phase_config)

        self.shape_names = ["Square", "Triangle", "Circle"]
        self.shape_images = {
            "SquareFriendly": pg.transform.smoothscale_by(pg.image.load("../Games/ShapeRoyale/Data/assets/Square_Sprite_Player.png"), 0.1).convert_alpha(),
            "SquareEnemy": pg.transform.smoothscale_by(pg.image.load("../Games/ShapeRoyale/Data/assets/Square_Sprite_Enemy.png"), 0.1).convert_alpha(),
            "TriangleFriendly": pg.transform.smoothscale_by(pg.image.load("../Games/ShapeRoyale/Data/assets/Triangle_Sprite_Player.png"), 0.1).convert_alpha(),
            "TriangleEnemy": pg.transform.smoothscale_by(pg.image.load("../Games/ShapeRoyale/Data/assets/Triangle_Sprite_Enemy.png"), 0.1).convert_alpha(),
            "CircleFriendly": pg.transform.smoothscale_by(pg.image.load("../Games/ShapeRoyale/Data/assets/Circle_Sprite_Player.png"), 0.1).convert_alpha(),
            "CircleEnemy": pg.transform.smoothscale_by(pg.image.load("../Games/ShapeRoyale/Data/assets/Circle_Sprite_Enemy.png"), 0.1).convert_alpha()
        }
        
        with open("../Games/ShapeRoyale/Data/shapes.json", "r") as f:
            self.shape_info = loads(f.read())

        with open("../Games/ShapeRoyale/Data/powerups.json", "r") as f:
            self.powerup_info = loads(f.read())

        self.bullets = []
        self.players = self.generate_players()
        self.powerups = self.generate_powerups()

        self.powerup_sections = [(i*self.POWERUP_SECTION_SIZE, (i+1)*self.POWERUP_SECTION_SIZE) for i in range(self.NUM_POWERUP_SECTIONS)]
        self.powerup_section_index = 0

        self.fps_font = pg.font.SysFont(f"{FONTS_PATH}/PressStart2P.ttf", 30)

        self.main()

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

    def generate_safezone_phases(self, num_phases: int) -> None:
        phase_config = {}

        radius = (self.MAP_SIZE * sqrt(2)) // 2
        target = (self.MAP_SIZE_X / 2, self.MAP_SIZE_Y / 2)
        time = 60/10

        time_reduction = time // num_phases

        for p in range(num_phases - 1):
            phase_config[p] = {
                "radius": radius,
                "target": target,
                "time": time
            }

            radius //= 2
            target = (randint(target[0] - radius, target[0] + radius), randint(target[1] - radius, target[1] + radius))
            time -= time_reduction

        phase_config[num_phases - 1] = {
            "radius": 0,
            "target": target,
            "time": 0
        }

        self.phase_config = phase_config

    def generate_players(self) -> List[Shape]:
        shapes = []

        for i, player in enumerate(self.main_menu.players):
            name = self.shape_names[player.shape_index]
            new_shape = Shape(
                randint(0, self.MAP_SIZE_X*0), randint(0, self.MAP_SIZE_Y*0), choice(self.shape_names), self.shape_info, self.shape_images[f"{name}Friendly"],
                self.shape_images[f"{name}Enemy"], self.bullets, self.bullet_img, True, self.controllers[i], []
            )
            new_shape.squad.append(new_shape)
            shapes.append(new_shape)

        for i in range(self.NUM_PLAYERS - len(self.main_menu.players)):
            name = choice(self.shape_names)
            new_shape = Shape(
                randint(0, self.MAP_SIZE_X), randint(0, self.MAP_SIZE_Y), choice(self.shape_names), self.shape_info, self.shape_images[f"{name}Friendly"],
                self.shape_images[f"{name}Enemy"], self.bullets, self.bullet_img, is_player=False, controller=None, squad=[]
            )
            new_shape.squad.append(new_shape)
            shapes.append(new_shape)

        return shapes

    def generate_powerups(self) -> List[Powerup]:
        powerups = []

        common_rarity_max = self.powerup_info["Common"]["spawn_chance"]
        uncommon_rarity_max = self.powerup_info["Uncommon"]["spawn_chance"]
        rare_rarity_max = self.powerup_info["Rare"]["spawn_chance"]
        legendary_rarity_max = self.powerup_info["Legendary"]["spawn_chance"]

        for i in range(self.NUM_POWERUPS):
            rarity_number = uniform(0.0, 1.0)

            if rarity_number <= legendary_rarity_max: rarity = "Legendary"
            elif rarity_number <= legendary_rarity_max + rare_rarity_max: rarity = "Rare"
            elif rarity_number <= legendary_rarity_max + rare_rarity_max + uncommon_rarity_max: rarity = "Uncommon"
            else: rarity = "Common"

            powerups.append(Powerup(randint(0, self.MAP_SIZE_X), randint(0, self.MAP_SIZE_Y), rarity, self.powerup_info, self.on_powerup_pickup))

        return powerups

    def on_powerup_pickup(self, powerup: Powerup) -> None:
        self.powerups.remove(powerup)
    
    def main(self) -> None:
        last_safezone_draw = 0
        while 1:
            dt = self.clock.tick(60) / 1000.0

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            self.safezone.update(dt)

            if time() - last_safezone_draw > 0.5:
                self.safezone.draw()
                last_safezone_draw = time()

            for s, screen in enumerate(self.screens):
                screen.fill((0, 0, 0))
                self.safezone.blit(screen, self.players[s])

            keys = pg.key.get_pressed()

            if keys[pg.K_UP]: self.players[0].move_up(dt)
            elif keys[pg.K_RIGHT]: self.players[0].move_right(dt)
            elif keys[pg.K_DOWN]: self.players[0].move_down(dt)
            elif keys[pg.K_LEFT]: self.players[0].move_left(dt)

            elif keys[pg.K_SPACE]: self.players[0].shoot()

            for player in self.players:
                player.update(dt)

                for s, screen in enumerate(self.screens):
                    player.draw(screen, self.players[s])


                    for bullet in self.bullets:
                        bullet.draw(screen, self.players[s])

                        if s == 0: # Just do it once
                            bullet.move(dt)

                            #if player.rect.colliderect(bullet.rect):
                            #    bullet.hit(player)

                            if bullet.distance_travelled > self.MAX_BULLET_TRAVEL_DIST:
                                self.bullets.remove(bullet)

                for powerup in self.powerups[self.powerup_sections[self.powerup_section_index][0]:self.powerup_sections[self.powerup_section_index][1]]:
                    powerup_dist_x = abs(powerup.x - player.x)
                    powerup_dist_y = abs(powerup.y - player.y)
    
                    if powerup_dist_x <= -1000 or powerup_dist_x >= 1000 or powerup_dist_y <= -1000 or powerup_dist_y >= 1000: continue

                    powerup_dist = dist((powerup.x, powerup.y), (player.x, player.y))

                    if powerup_dist <= player.rect.w:
                        powerup.pickup(player)
                    
                    powerup.draw(screen, self.players[s])

            for s, screen in enumerate(self.screens):
                for powerup in self.powerups:
                    powerup.draw(screen, self.players[s])

                self.display_surf.blit(screen, screen.pos)

            self.display_surf.blit(self.fps_font.render(f"{self.clock.get_fps():.2f}", True, (255, 255, 255)), (20, 20))

            self.powerup_section_index += 1
            if self.powerup_section_index >= self.NUM_POWERUP_SECTIONS: self.powerup_section_index = 0

            pg.display.flip()