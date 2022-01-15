import pygame
import pytmx
from levels import Room
import const
import interfaces


class Entity(pygame.sprite.Sprite):
    def __init__(
            self,
            object_tmx: pytmx.TiledObject,
            room: Room,
            *groups
    ):
        super().__init__(*groups)
        self.room = room
        self.__object_tmx = object_tmx
        points = object_tmx.apply_transformations()
        coord = self.room.convert_coord(*points[0])
        if room.get_tile_properties(*coord)['type'] == const.TYPE_BLOCK_WALL:
            self.kill()
            return
        self.rect = pygame.Rect(
            (
                coord[1] * room.get_map().tileheight,
                coord[0] * room.get_map().tilewidth
            ),
            (object_tmx.width, object_tmx.height)
        )
        if object_tmx.image is not None:
            self.image = pygame.transform.smoothscale(
                object_tmx.image, self.rect.size
            )
        else:
            self.image = pygame.Surface(self.rect.size)

    def move(
            self,
            direction: tuple[int | float, int | float]
    ):
        """Перемещение игрока."""
        x_direction, y_direction = direction
        map_room = self.room.get_map()
        # Сдвиг координат.
        k_x = x_direction * map_room.tilewidth
        k_y = y_direction * map_room.tileheight
        new_rect = self.rect.move(k_x, k_y)
        coord = self.room.convert_coord(*new_rect.topleft)
        if not self.room.check_correct_row_col(*coord):
            return
        if self.room.get_tile_properties(*coord)['type'] == const.TYPE_BLOCK_WALL:
            return
        self.rect.move_ip(k_x, k_y)

    def update_property(self, object_tmx, room, *group):
        self.__init__(object_tmx, room, *group)


class Player(Entity):
    def __init__(
            self,
            object_tpx,
            room: Room,
            *groups
    ):
        super().__init__(object_tpx,
                         room,
                         *groups)
        self.current_weapon = None
        self.health_capacity = 100
        self.current_health = 100

    def get_screen_player(self, width, height):
        x, y = self.rect.center
        screen_player = pygame.Rect(
            (x - width / 2, y - height / 2),
            (width, height)
        )
        return screen_player

    def start_battle(self, mob, game):
        interfaces.templates.InterfaceBattle(game.battle_interface, game, self, mob)


class Item(Entity):
    def __init__(self, object_tmx, room, *groups):
        super().__init__(object_tmx, room, *groups)
        self.damage = 20

    def update(self, player):
        coord_player = self.room.convert_coord(*player.rect.topleft)
        coord_mob = self.room.convert_coord(*self.rect.topleft)
        if coord_player[0] == coord_mob[0] and coord_player[1] == coord_mob[1]:
            player.current_weapon = self
            self.kill()


class Mob(Entity):
    def __init__(self, object_tmx, room: Room, *groups):
        super().__init__(object_tmx, room, *groups)
        self.health_capacity = 100
        self.current_health = 100
        self.current_weapon = None

    def update(self, player, game):
        coord_player = self.room.convert_coord(*player.rect.topleft)
        coord_mob = self.room.convert_coord(*self.rect.topleft)
        if coord_player[0] == coord_mob[0] and coord_player[1] == coord_mob[1]:
            player.start_battle(self, game)


class NPC(Entity):
    def __init__(self, object_tmx, room: Room, *groups):
        super().__init__(object_tmx, room, *groups)
        self.interface = None

    def update(self, player, game):
        coord_player = self.room.convert_coord(*player.rect.topleft)
        coord_mob = self.room.convert_coord(*self.rect.topleft)
        if coord_player[0] == coord_mob[0] and coord_player[1] == coord_mob[1]:
            interfaces.templates.InterfaceTeleport(game.battle_interface, game, player)

    def set_interface(self, interface):
        self.interface = interface

    def display_interface(self, manager):
        self.interface(manager)







