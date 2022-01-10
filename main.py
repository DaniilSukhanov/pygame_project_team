import os

import pygame
import pytmx
import const
from entitys import Entity, Player


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
        # Карта комнаты.
        if type(filename_map) != str:
            raise TypeError(
                'Был передан не правильный тип данных ('
                f'должно быть str, а не {type(filename_map)}).'
            )
        # Карта комнаты.
        self.__map = pytmx.load_pygame(filename_map)

    def __repr__(self):
        return f'{self.__class__} ({self.__map.properties["type"]})'

    def convert_coord(self, x: float | int, y: float | int):
        """Конвертирует координаты формата x и y
        в координаты формата row и col"""
        if type(x) not in {float, int}:
            raise TypeError(
                'Аргумент x должен быть float, int,'
                f' а не {type(x)}'
            )
        if type(y) not in {float, int}:
            raise TypeError(
                'Аргумент y должен быть float, int,'
                f' а не {type(y)}'
            )
        return y // self.__map.tileheight, x // self.__map.tilewidth

    def check_correct_x_y(self, x: float | int, y: float | int):
        """Проверяет корректность координат в формате x и y."""
        row, col = self.convert_coord(x, y)
        if self.check_correct_row_col(row, col):
            return True
        return False

    def draw(self, screen: pygame.Surface):
        """Рисует карту на screen."""
        if not isinstance(screen, pygame.Surface):
            raise TypeError(
                'Аргумент screen не принадлежит типу Surface, а'
                f' принадлежит к {type(screen)}'
            )
        for row in range(self.__map.width):
            for col in range(self.__map.height):
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
        """Проверка корректности координат в формате row и col."""
        if row in range(self.__map.height) and col in range(self.__map.height):
            return True
        return False

    def get_tile_range_connection_blocks(
            self,
            point1: tuple[int | float, int | float] | list[int, float],
            point2: tuple[int | float, int | float] | list[int, float],
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
        """Возвращает прямоугольник клетки по координатам row и col"""
        return pygame.Rect(
            (col * self.__map.tilewidth, row * self.__map.tileheight),
            (self.__map.width, self.__map.height)
        )

    def get_map(self):
        """Возвращает копию карты (пересоздание)."""
        return self.__map


class Level:
    def __init__(self, count_rows: int, count_cols: int):
        # Матрица, в которой будут располагаться комнаты.
        self.__matrix = list(
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
        self.__count_rows = count_rows
        self.__count_cols = count_cols
        # Координаты текущей комнаты.
        self.__coord_current_room = None

    def set_matrix(
            self,
            matrix: list[list[None | Room]],
            coord_current_room: tuple[int, int]
    ):
        """Ставить новую матрицу."""
        if type(matrix) != list:
            raise TypeError(
                f'Аргумент matrix должен быть list, а не {type(matrix)}.'
            )
        if not matrix:
            raise ValueError('Аргумент matrix не должен быть пустым.')
        if set(
            filter(
                lambda element: type(element) != list,
                matrix
            )
        ):
            raise TypeError(
                'Какой-то элемент аргумента matrix не list.'
            )
        if tuple(
            filter(
                lambda element1: set(
                    filter(
                        lambda element2: type(element2) not in {
                            type(None), Room
                        },
                        element1
                    )
                ),
                matrix
            )
        ):
            raise TypeError(
                'Элементы элементов аргумента matrix должны быть Room, None.'
            )
        if len(set(
            map(
                lambda element: len(element),
                matrix
            )
        )) != 1:
            raise ValueError(
                'Длина элементов аргумента matrix должна быть одинаковой.'
            )
        self.__matrix = matrix
        self.__count_rows = len(matrix)
        self.__count_cols = len(matrix[0])
        self.__coord_current_room = coord_current_room

    def __check_error_correction_coord(self, row: int, col: int):
        """Проверка на корректность координат. Если что-то не правильно, то
        возбуждается ошибка."""
        if int != type(row):
            raise TypeError(
                f'Переданный тип значения в аргументе row не int,'
                f' а {type(row)}'
            )
        if int != type(col):
            raise TypeError(
                f'Переданный тип значения в аргументе col не int,'
                f' а {type(col)}'
            )
        if row in range(self.__count_rows) and col in range(self.__count_cols):
            raise ValueError(
                f'Переданные координаты ({row}, {col}) не попадают в диапазон'
                f'(0 <= row < {self.__count_rows},'
                f' 0 <= col < {self.__count_cols}).'
            )

    def check_correction_coord(self, row: int, col: int) -> bool:
        """Проверка на корректность координат."""
        try:
            self.__check_error_correction_coord(row, col)
            return True
        except ValueError:
            return False

    def set_room(self, room: Room, row: int, col: int):
        """Ставит комнату на координаты row и col."""
        if type(room) != Room:
            raise ValueError('Переданная комната - не комната.')
        self.__check_error_correction_coord(row, col)
        self.__matrix[row][col] = room

    def set_current_room(self, row: int, col: int):
        """Меняет текущую комнату на комнату, которая находиться
        в матрицы по координатам row и col"""
        self.__check_error_correction_coord(row, col)
        self.__coord_current_room = None if self.__matrix[row][
                                                col] is None else (
            row, col
        )

    def get_room(self, row: int, col: int) -> None | Room:
        """Получить комнату по координатам."""
        self.__check_error_correction_coord(row, col)
        """Получить комнату по координатам формата row и col."""
        return self.__matrix[row][col]

    def get_current_room(self) -> None | Room:
        """Получить текущую комнату."""
        row, col = self.__coord_current_room
        return self.get_room(row, col)

    def displace_current_room(self, k_row: int, k_col: int):
        """Смещает текущую комнату на k_row, k_col."""
        if type(k_row) != int:
            raise TypeError(
                'Переданный тип значения аргумента k_row не int, а '
                f'{type(k_row)}.'
            )
        if type(k_col) != int:
            raise TypeError(
                'Переданный тип значения аргумента k_col не int, а '
                f'{type(k_col)}.'
            )
        row_current_room, col_current_room = self.__coord_current_room
        row_current_room += k_row
        col_current_room += k_col
        try:
            self.__check_error_correction_coord(
                row_current_room, col_current_room
            )
            if self.get_room(row_current_room, col_current_room) is not None:
                self.__coord_current_room = (
                    row_current_room, col_current_room
                )
                return True
        except Exception:
            return False


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
    player = Player(map_room.get_object_by_name('player'), group)
    for i in map_room.objects:
        if i.type == 'player':
            continue
        Entity(i, group)

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
        if keys[pygame.K_UP]:
            player.move(room, (0, -1))
        if keys[pygame.K_DOWN]:
            player.move(room, (0, 1))
        if keys[pygame.K_LEFT]:
            player.move(room, (-1, 0))
        if keys[pygame.K_RIGHT]:
            player.move(room, (1, 0))
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
