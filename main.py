import os

import pygame
import const
from entitys import Mob, Player
from levels import Room
import pygame_gui
from interfaces.interface import Interface
from interfaces.templates import *


class SpritesGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.disabled = False

    def update(self, *args, **kwargs):
        if not self.disabled:
            for sprite in self.sprites():
                sprite.update(*args, **kwargs)


def load_image(name: str, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        raise FileNotFoundError(f"Файл с изображением '{fullname}' не найден")
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Game:
    def __init__(self):
        self.main_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.main_interface = Interface(
            self.main_screen.get_size(), 10, 10
        )
        self.battle_interface = Interface(
            self.main_screen.get_size(), 20, 20
        )
        self.__cycle()

    def __cycle(self):
        player_screen = pygame.Surface(self.main_screen.get_size())
        room = Room('data/templates_maps/map1.tmx')
        group1 = SpritesGroup()
        group2 = SpritesGroup()
        map_room = room.get_map()
        player = Player(map_room.get_object_by_name('player'), room, group1)
        InterfaceStartGame(self.main_interface, self.main_screen)
        InterfacePlayer(self.main_interface, player)
        for i in map_room.objects:
            if i.type == 'player':
                continue
            Mob(i, room, group2)
        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(const.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and
                        event.key == pygame.K_ESCAPE
                ):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        player.move((0, -1))
                    elif event.key == pygame.K_DOWN:
                        player.move((0, 1))
                    elif event.key == pygame.K_LEFT:
                        player.move((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        player.move((1, 0))
                    group1.update(player)
                    group2.update(player, self)
                self.main_interface.event_elements(event)
                self.battle_interface.event_elements(event)

            self. main_screen.fill('black')
            player_screen.fill('black')
            room.draw(player_screen)
            group1.draw(player_screen)
            group2.draw(player_screen)
            self.main_interface.update(time_delta)
            self.battle_interface.update(time_delta)

            self.main_screen.blit(
                player_screen, (0, 0), player.get_screen_player(
                    *player_screen.get_size()
                )
            )
            self.main_interface.draw_ui(self.main_screen)
            self.battle_interface.draw_ui(self.main_screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    pygame.init()
    Game()
