import os
import sqlite3
import pytmx


class DataBase:
    def __new__(cls, *args, **kwargs):
        """Паттерн Singleton."""
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
                room = pytmx.load_pygame(path_file)
                if result is None:
                    self.cur.execute(
                        """
                        INSERT INTO templates_rooms(
                            type_template_room, path_template_room,
                            width_template_room, height_template_room
                        ) VALUES (?, ?, ?, ?)
                        """, (
                            room.properties['type'], path_file,
                            room.width, room.height
                        )
                    )
                    self.con.commit()

    def delete_room(self, path):
        """Удаляет комнату по пути."""
        self.cur.execute(
            """
            DELETE from templates_rooms WHERE path_template_room = ?
            """,
            (path,)
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

    def get_rooms_by_type(self, type_room: str | None = None):
        """Получить комнату по типу."""
        if type_room is not None:
            result = self.cur.execute(
                """
                SELECT path_template_room FROM templates_rooms
                WHERE type_template_room = ?
                """,
                (type_room,)
            ).fetchall()
        else:
            result = self.cur.execute(
                """SELECT path_template_room FROM templates_rooms"""
            ).fetchall()
        return result

    def get_items(self):
        """Получить предметы."""
        result = self.cur.execute(
            """
            SELECT name, image, damage FROM items
            """
        ).fetchall()
        return result
