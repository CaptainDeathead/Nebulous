import pygame as pg

from typing import List

class Blank:
    def __init__(self, display_surf: pg.Surface, console_update: object, get_num_players: object, controllers: List) -> None:
        self.display_surf = display_surf
        self.console_update = console_update

        self.clock = pg.time.Clock()

        self.font = pg.font.SysFont(None, 20)

        self.main()

    def main(self) -> None:
        while 1:
            dt = self.clock.tick(60)

            self.display_surf.fill((0, 0, 0))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

            self.console_update()

            self.display_surf.blit(self.font.render(str(self.clock.get_fps()), True, (255, 255, 255)), (20, 20))

            pg.display.flip()

if __name__ == "__main__":
    pg.init()
    Blank(pg.display.set_mode((1920, 1080), pg.HWSURFACE | pg.SRCALPHA), lambda: None, None, None)