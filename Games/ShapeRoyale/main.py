import pygame as pg

from Console.Controllers.controller import Controller, CONTROLS
from Console.sound import generate_sine_wave

from time import time
from json import loads
from math import dist

from typing import List, Sequence, Dict

FONTS_PATH = "./UI/Fonts"

class Poison:
    def __init__(self, deal_damage_func: object, on_poison_end: object, damage: int, duration: int) -> None:
        self.deal_damage_func = deal_damage_func
        self.on_poison_end = on_poison_end

        self.damage = damage
        self.duration = duration

        self.last_tick_time = time()

    def update(self) -> None:
        if time() - self.last_tick_time >= 1:
            self.duration -= time() - self.last_tick_time
            self.last_tick_time = time()

            self.deal_damage_func(self.damage)

            if self.duration <= 0: self.on_poison_end(self)

class Bullet:
    def __init__(self, parent: any, x: float, y: float, velocity: List[float, float], base_damage: int, damage_growth: float, poison_damage: int, penetration: float) -> None:
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

    @property
    def distance_travelled(self) -> float:
        return dist(self.x - self.start_x, self.y - self.start_y)

    def move(self, dt: float) -> None:
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

    def hit(self, target: any) -> None:
        health_damage = self.base_damage * (self.damage_growth * self.distance_travelled)
        shield_damage = health_damage * self.penetration

        target.take_damage(health_damage)
        target.take_shield_damage(shield_damage)

        if self.poison_damage > 0:
            target.add_poison(self.poison_damage)

class Shape:
    POISON_DURATION = 10

    def __init__(self, x: float, y: float, shape_name: str, shape_info: Dict[str, Dict], shape_image: pg.Surface, bullets: List[Bullet],
                 is_player: bool, controller: Controller | None = None) -> None:

        self.x = x
        self.y = y

        self.shape_name = shape_name
        self.shape_info = shape_info
        self.info = self.shape_info[self.shape_name]

        self.shape_image = shape_image

        self.is_player = is_player
        self.controller = controller

        self.max_hp = self.info['hp'] # literal
        self.max_shield = self.info['shield'] # literal
        self.max_speed = self.info['speed'] # literal
        self.damage = self.info['damage'] # literal
        self.firerate = self.info['firerate'] # literal 
        self.bullet_speed = self.info['bullet_speed'] # literal
        self.penetration = self.info['penetration'] # percent
        self.shield_regen = self.info['shield_regen'] # literal
        self.lifesteal = 1.0 # percent
        self.poison_damage = 0 # literal
        self.zone_resistance = 1.0 # percent
        self.health_regen_rate = self.info["health_regen"] # literal
        self.damage_growth = 1.0 # percent

        self.hp = self.max_hp
        self.shield = self.max_shield

        self.velocity = [0.0, 0.0]

        self.last_shoot_time = 0

        self.bullets = bullets

    def change_var_value(var: object, value_type: str, value: any) -> None:
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
                case 'penetration': var = self.bullet_penetration
                case 'shieldregenrate': var = self.shield_regen_rate
                case 'lifesteal': var = self.lifesteal
                case 'poisondamage': var = self.poison_damage
                case 'zoneresistance': var = self.zone_resistance
                case 'healthregenrate': var = self.health_regen_rate
                case 'damagegrowth': var = self.damage_growth

            self.change_var_value(var, args[2], value)

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

    def add_poison(self, poison_damage: int) -> None:
        self.poisons.append(Poison(self.take_damage, self.on_poison_end, poison_damage, self.POISON_DURATION))

    def move_up(self) -> None:
        self.velocity[1] = -self.max_speed
        self.rotation = 0

    def move_right(self) -> None:
        self.velocity[0] = self.max_speed
        self.rotation = 90

    def move_down(self) -> None:
        self.velocity[1] = self.max_speed
        self.rotation = 180

    def move_left(self) -> None:
        self.velocity[0] = -self.max_speed
        self.rotation = 270

    def shoot(self) -> None:
        if time() - self.last_shoot_time >= 1 / self.firerate:
            self.last_shoot_time = time()

            if self.velocity[0] == 0 and self.velocity[1] == 0:
                match self.rotation:
                    case 0: bullet_vel = [0, -self.max_speed * (self.bullet_speed + 1)]
                    case 90: bullet_vel = [-self.max_speed * (self.bullet_speed + 1), 0]
                    case 180: bullet_vel = [0, self.max_speed * (self.bullet_speed + 1)]
                    case 270: bullet_vel = [self.max_speed * (self.bullet_speed + 1), 0]
            else: 
                bullet_vel = [self.velocity[0] * (self.bullet_speed + 1), self.velocity[1] * (self.bullet_speed + 1)]

            self.bullets.append(Bullet(self, self.x, self.y, bullet_vel, self.damage, self.damage_growth, self.poison_damage, self.penetration))

    def update(self, dt: float) -> None:
        if self.is_player:
            for event in self.controller.event.get():
                if event.type == CONTROLS.DPAD.UP: self.move_up()
                elif event.type == CONTROLS.DPAD.RIGHT: self.move_right()
                elif event.type == CONTROLS.DPAD.DOWN: self.move_down()
                elif event.type == CONTROLS.DPAD.LEFT: self.move_left()

                elif event.type == CONTROLS.ABXY.B: self.shoot()
        else:
            self.ai_move()

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

class MainMenu:
    TIMER_LENGTH = 6

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
                self.fonts["small"].render(f"Speed: {shape_speed}u/s", True, (255, 255, 255))
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

    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List[Controller]) -> None:
        self.display_surf = display_surf
        self.console_update = console_update
        self.get_num_players = get_num_players
        self.controllers = controllers

        self.main_menu = MainMenu(self.display_surf, self.console_update, self.controllers)

        self.num_screens = self.get_num_players()

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
            dt = self.clock.tick(60)

            for event in pg.event.get():
                ...

            ...