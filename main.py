import os

import pygame
import const
from entitys import Mob, Player
from levels import Room


class GroupContainer:
    """Класс написан на паттерне Singleton."""
    __instance = None
    __groups = {}

    def __new__(cls):
        if not hasattr(cls, '__instance'):
            cls.__instance = super(GroupContainer, cls).__new__(cls)
        return cls.__instance

    def draw_group(self, screen, key):
        self.__groups[key].draw(screen)

    def add_group(self, key, group):
        self.__groups[key] = group

    def remove_group(self, key):
        del self.__groups[key]

    def get_group(self, key):
        return self.__groups[key]

    def get_all_groups(self):
        return self.__groups.values()

    def draw(self, screen):
        for group in self.__groups.values():
            group.draw(screen)


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


def main():
    pygame.init()
    main_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    player_screen = pygame.Surface(main_screen.get_size())
    room = Room('data/templates_maps/map2.tmx')
    group = SpritesGroup()
    map_room = room.get_map()
    player = Player(map_room.get_object_by_name('player'), room, group)
    for i in map_room.objects:
        if i.type == 'player':
            continue
        Mob(i, room, group)

    clock = pygame.time.Clock()
    running = True
    while running:
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
                group.update(player)
        main_screen.fill('black')
        player_screen.fill('black')
        room.draw(player_screen)
        group.draw(player_screen)
        main_screen.blit(player_screen, (0, 0), player.get_screen_player(*player_screen.get_size()))
        pygame.display.flip()
        clock.tick(const.FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
