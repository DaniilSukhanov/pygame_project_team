import os
import sqlite3
from bs4 import BeautifulSoup


class DataBase:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, filename: str):
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor()

    def load_templates_rooms(self):
        """Загружает шаблоны карт в базу данных."""
        for root, _, files in os.walk("data/templates_maps"):
            files = filter(
                lambda element: '.tmx' in element,
                files
            )
            for filename in files:
                path_file = f'{root}/{filename}'
                result = self.cur.execute(
                    """
                    SELECT template_room_id FROM templates_rooms
                    WHERE path_template_room = ?
                    """, (path_file,)
                ).fetchone()
                parser = Parse(path_file)
                properties = parser.get_properties()
                if result is None:
                    self.cur.execute(
                        """
                        INSERT INTO templates_rooms(
                            type_template_room, path_template_room,
                            width_template_room, height_template_room
                        ) VALUES (?, ?, ?, ?)
                        """, (
                            properties['type'], path_file,
                            properties['width'], properties['height']
                        )
                    )
                    self.con.commit()

    def load_save(self, name: str, save):
        """Загружает в базу данных сохранение."""
        self.cur.execute(
            """
            INSERT INTO saves (title_save, data_save)
            VALUES (?, ?)
            """,
            (name, save)
        )
        self.con.commit()


class Parse:
    def __init__(self, filename):
        self.soup = BeautifulSoup(
            open(filename).read(), 'lxml'
        )

    def get_properties(self) -> dict:
        """Возвращает словарь с нужными свойствами карты."""
        result = {}
        properties = self.soup.find('properties')
        properties = filter(
            lambda element: element['name'] == 'type',
            properties.find_all('property')
        )
        for i in properties:
            result[i['name']] = i['value']
        map_tag = self.soup.find('map')
        result['width'] = map_tag['width']
        result['height'] = map_tag['height']
        return result


data_base = DataBase('data_base.sqlite')
data_base.load_templates_rooms()
