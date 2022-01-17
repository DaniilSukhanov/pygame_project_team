import random
import os

from data_base import DataBase
from levels import Room


class Generator:
    def __init__(
            self,
            count_rows: int,
            count_cols: int,
            sure_generate_type_rooms: dict[str: int] | None = None
    ):
        self.__count_rows = count_rows
        self.__count_cols = count_cols
        if sure_generate_type_rooms is not None:
            free_places = count_rows * count_cols - sum(
                sure_generate_type_rooms.values()
            )
            if free_places < 0:
                raise ValueError(
                    "Переданный словарь некорректен, так как кол-во "
                    "обязательных "
                    "для генерации комнат больше, чем мест на карте. "
                    "Увеличьте размер карты."
                )
        else:
            free_places = count_rows * count_cols
        self.__free_places = free_places
        self.__sure_generation_type_rooms = sure_generate_type_rooms

    def generate(self) -> list[list[Room]]:
        """Генерация уровня."""
        return self.__generate_room_layouts()

    def __generate_matrix(self) -> dict:
        """Генерация матрицы."""
        matrix = list(
            map(
                lambda _: [None] * self.__count_cols,
                range(self.__count_rows)
            )
        )
        matrix_places = {
            (i, j) for i in range(self.__count_rows)
            for j in range(self.__count_cols)
        }
        return {'matrix': matrix, 'places': matrix_places}

    def __generate_room_layouts(self):
        """Генерация матрицы с комнатами."""
        matrix = self.__generate_matrix()
        if self.__sure_generation_type_rooms is not None:
            for type_room, count in self.__sure_generation_type_rooms.items():
                for _ in range(count):
                    row, col = matrix['places'].pop()
                    room = self.__random_room(type_room)
                    matrix['matrix'][row][col] = room
        for _ in range(self.__free_places):
            row, col = matrix['places'].pop()
            room = self.__random_room()
            matrix['matrix'][row][col] = room
        return matrix['matrix']

    @staticmethod
    def __random_room(type_room: str | None = None):
        """Получить случайную комнату."""
        data_base = DataBase('data_base.sqlite')
        while True:
            rooms = data_base.get_rooms_by_type(type_room)
            path_room = random.choice(rooms)[0]
            if os.path.isfile(path_room):
                break
            data_base.delete_room(path_room)
        return Room(path_room)
