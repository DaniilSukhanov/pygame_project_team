import pygame
import const
import pytmx


class Entity(pygame.sprite.Sprite):
    def __init__(
            self,
            object_tmx: pytmx.TiledObject,
            *groups
    ):
        super().__init__(*groups)
        self.__object_tmx = object_tmx
        points = object_tmx.apply_transformations()
        self.rect = pygame.Rect(
            points[0],
            (object_tmx.width, object_tmx.height)
        )
        if object_tmx.image is not None:
            self.image = pygame.transform.smoothscale(
                object_tmx.image, self.rect.size
            )
        else:
            self.image = pygame.Surface(self.rect.size)


class Player(Entity):
    def __init__(
            self,
            object_tpx,
            *groups
    ):
        super().__init__(object_tpx,
                         *groups)
        self.speed = 150 / const.FPS

    def get_screen_player(self, width, height):
        x, y = self.rect.center
        screen_player = pygame.Rect(
            (x - width / 2, y - height / 2),
            (width, height)
        )
        return screen_player

    def move(
            self,
            room,
            direction: tuple[int | float, int | float]
    ):
        """Перемещение игрока."""
        x_direction, y_direction = direction
        # Сдвиг координат.
        k_x = x_direction * self.speed
        k_y = y_direction * self.speed
        self.rect.move_ip(k_x, k_y)


class Mob(Entity):
    def __init__(self, object_tmx, *groups):
        super().__init__(object_tmx, *groups)


class NPC(Entity):
    def __init__(self, object_tmx, *groups):
        super().__init__(object_tmx, *groups)
        self.interface = None

    def set_interface(self, interface):
        self.interface = interface

    def display_interface(self, manager):
        self.interface(manager)







