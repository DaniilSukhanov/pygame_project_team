import copy
import os
import random
import sys

import pygame
import pytmx
import const


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


class Room:
    def __init__(
            self,
            filename_map: str
    ):
        self.__map = pytmx.load_pygame(filename_map)

    def convert_coord(self, x: float | int, y: float | int):
        return y // self.__map.tileheight, x // self.__map.tilewidth

    def check_correct_x_y(self, x: float | int, y: float | int):
        row, col = x // const.SIZE_BLOCK, y // const.SIZE_BLOCK
        if self.check_correct_row_col(row, col):
            return True
        return False

    def draw(self, screen: pygame.Surface):
        for row in range(self.__map.height):
            for col in range(self.__map.width):
                image = self.__map.get_tile_image(row, col, 0)
                if image is not None:
                    screen.blit(
                        image,
                        (
                            row * self.__map.tilewidth,
                            col * self.__map.tilewidth
                        )
                    )

    def check_correct_row_col(self, row: int, col: int):
        if row in range(self.__map.height) and col in range(self.__map.height):
            return True
        return False

    def get_tile_range_connection_blocks(
            self,
            point1,
            point2,
            type_tile: str
    ):
        """Возвращает первую попавшеюся клетку, которая находиться в
        диапазоне 2-х точек и имеет type_tile."""
        if point1[0] == point2[0]:
            row = point1[0]
            step = 1 if point1[1] <= point2[1] else -1
            for i in range(point1[1], point2[1] + step, step):
                tile = self.get_tile_properties(row, i)
                if tile is not None and tile['type'] == type_tile:
                    return self.get_tile_rect(row, i)
        elif point1[1] == point2[1]:
            col = point1[1]
            step = 1 if point1[0] <= point2[0] else -1
            for i in range(point1[0], point2[0] + step, step):
                tile = self.get_tile_properties(i, col)
                if tile is not None and tile['type'] == type_tile:
                    return self.get_tile_rect(i, col)
        else:
            raise ValueError('Одна из координат должна быть одинаковой.')

    def get_tile_properties(self, row: int, col: int, layer=0) -> dict | None:
        """Возвращает словарь свойств клетки."""
        try:
            result = self.__map.get_tile_properties(col, row, layer)
        except Exception:
            result = None
        return result

    def get_tile_rect(self, row: int, col: int):
        return pygame.Rect(
            (col * self.__map.tilewidth, row * self.__map.tileheight),
            (self.__map.width, self.__map.height)
        )

    def get_map(self):
        return pytmx.load_pygame(self.__map.filename)


class Level:
    def __init__(self, count_rows: int, count_cols: int):
        self.matrix = list(
            map(
                lambda _: list(
                    map(
                        lambda _: None,
                        range(count_cols)
                    )
                ),
                range(count_rows)
            )
        )
        self.count_rows = count_rows
        self.count_cols = count_cols
        self.coord_current_room = None

    def check_correction_coord(self, row: int, col: int) -> bool:
        if row in range(self.count_rows) and col in range(self.count_cols):
            return True
        return False

    def set_room(self, room: Room, row: int, col: int):
        self.matrix[row][col] = room

    def set_current_room(self, row: int, col: int):
        self.coord_current_room = None if self.matrix[row][col] is None else (
            row, col
        )

    def get_room(self, row: int, col: int) -> None | Room:
        return self.matrix[row][col]

    def get_current_room(self) -> None | Room:
        row, col = self.coord_current_room
        return self.get_room(row, col)

    def displace_current_room(self, k_row: int, k_col: int):
        row_current_room, col_current_room = self.coord_current_room
        row_current_room += k_row
        col_current_room += k_col
        if (
                self.check_correction_coord(row_current_room,
                                            col_current_room) and
                self.get_room(row_current_room, col_current_room) is not None
        ):
            self.coord_current_room = (row_current_room, col_current_room)
            return True
        return False


class Entity(pygame.sprite.Sprite):
    def __init__(
            self,
            x: int | float,
            y: int | float,
            size_entity: float | int,
            image: pygame.Surface,
            speed_move: float | int,
            hp: int,
            name: str,
            *groups
    ):
        super().__init__(*groups)
        self.angle_view = 0
        self.speed = speed_move / const.FPS
        self.name = name
        self.hp = hp
        self.size_entity = size_entity
        self.rect = pygame.Rect(
            *map(lambda coord: coord - size_entity / 2, (x, y)),
            self.size_entity, self.size_entity
        )
        self.image = pygame.transform.smoothscale(image, self.rect.size)

    def set_position(self, x, y):
        self.rect.center = (x, y)


class Player(Entity):
    def __init__(
            self,
            x: float | int,
            y: float | int,
            size_entity: float | int,
            image: pygame.Surface,
            speed_move: float | int,
            hp: int,
            name: str,
            *groups
    ):
        super().__init__(x, y, size_entity, image, speed_move, hp, name,
                         *groups)

    def get_screen_player(self, width, height):
        x, y = self.rect.center
        screen_player = pygame.Rect(
            (x - width / 2, y - height / 2),
            (width, height)
        )
        return screen_player

    def update(self, *args, **kwargs):
        self.move(*args, **kwargs)

    def move(
            self,
            room: Room,
            direction: tuple[int | float, int | float]
    ):
        """Перемещение игрока."""
        x_direction, y_direction = direction
        # Сдвиг координат.
        k_x = x_direction * self.speed
        k_y = y_direction * self.speed
        # Перебираем стороны по направлению (+row -> правая сторона)
        for i, line in enumerate(self.__get_coord_line_rect_by_direction(
                self.rect, direction
        )):
            if line is None:
                continue
            # Получаем клетку, которая является стеной.
            connection_tile = room.get_tile_range_connection_blocks(
                *map(
                    lambda coord: room.convert_coord(*coord),
                    line
                ),
                const.TYPE_BLOCK_WALL
            )
            if connection_tile is not None:
                # Получаем противоположную по взгляду сторону (клетки)
                opposite_sides_direction = \
                    self.__get_coord_line_rect_by_direction(
                        connection_tile,
                        tuple(map(lambda x: -x, direction))
                    )
                if not i:
                    x2 = line[0][0]
                    x1 = opposite_sides_direction[0][0][0]
                    k_x = x1 - x2
                else:
                    y2 = line[1][1]
                    y1 = opposite_sides_direction[1][1][1]
                    k_y = y1 - y2
        self.rect.move_ip(k_x, k_y)

    @staticmethod
    def __get_coord_line_rect_by_direction(
            rect: pygame.Rect,
            direction: tuple[int | float, int | float]
    ):
        result = []
        if direction[0]:
            if direction[0] > 0:
                line = (
                    rect.topright,
                    rect.bottomright
                )
            else:
                line = (
                    rect.topleft,
                    rect.bottomleft
                )
        else:
            line = None
        result.append(line)
        if direction[1]:
            if direction[1] > 0:
                line = (
                    rect.bottomleft,
                    rect.bottomright
                )
            else:
                line = (
                    rect.topleft,
                    rect.topright
                )
        else:
            line = None
        result.append(line)
        return result


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
    room = Room('data/templates_maps/test_map.tmx')
    group = SpritesGroup()
    player = Player(
        510, 500, 30, load_image('hero.png', -1), 60, 0, '12', group
    )
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and
                    event.key == pygame.K_ESCAPE
            ):
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move(room, (0, -1))
        if keys[pygame.K_a]:
            player.move(room, (-1, 0))
        if keys[pygame.K_s]:
            player.move(room, (0, 1))
        if keys[pygame.K_d]:
            player.move(room, (1, 0))
        main_screen.fill('black')
        player_screen.fill('black')
        room.draw(player_screen)
        group.draw(player_screen)
        main_screen.blit(player_screen, (0, 0),
                         player.get_screen_player(*player_screen.get_size()))
        pygame.display.flip()
        clock.tick(const.FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
