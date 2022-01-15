import pygame
import data_base
import random


class Item:
    def __init__(
            self,
            name: str,
            image: pygame.Surface,
            damage: int
    ):
        self.name = name
        self.image = image
        self.damage = damage

    def __repr__(self):
        return f'Item: "{self.name}", {self.image}, {self.damage}'


class RandomizerItems:
    def __init__(self, filename_database: str):
        self.db = data_base.DataBase(filename_database)

    def get_item(self):
        items = self.db.get_items()
        if items:
            data = random.choice(items)
            item = Item(*data)
        else:
            item = None
        return item
