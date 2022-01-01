import os
import random
import sys

import pygame
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


class Block(pygame.sprite.Sprite):
    def __init__(
            self,
            row: int,
            col: int,
            image: pygame.Surface,
            type_block: str,
            *groups
    ):
        super().__init__(*groups)
        self.row, self.col = row, col
        self.rect = pygame.Rect(
            *map(
                lambda coord: coord * const.SIZE_BLOCK, (col, row)
            ),
            const.SIZE_BLOCK, const.SIZE_BLOCK
        )
        self.image = pygame.transform.smoothscale(image, self.rect.size)
        self.type_block = type_block

    def __repr__(self):
        return f'Block({self.row}, {self.col}) -> {self.type_block=}, {self.image=}'


class Room:
    def __init__(
            self,
            count_rows_area: int,
            count_cols_area: int
    ):
        self.count_cols = count_cols_area + 2
        self.count_rows = count_rows_area + 2
        self.group_room = SpritesGroup()
        GroupContainer().add_group(self, self.group_room)
        self.width = self.count_cols * const.SIZE_BLOCK
        self.height = self.count_rows * const.SIZE_BLOCK
        wall = load_image('brick.png', -1)
        void = load_image('cobblestone.png', -1)
        self.matrix = list(
            map(
                lambda i: list(
                    map(
                        lambda j: Block(
                            i, j, *(wall, const.TYPE_BLOCK_WALL)
                            if i in {0, self.count_rows - 1} or
                            j in {0, self.count_cols - 1} else
                            (void, const.TYPE_BLOCK_VOID),
                            self.group_room
                        ),
                        range(self.count_cols)
                    )
                ),
                range(self.count_rows)
            )
        )

    def set_block(self, block: Block):
        row, col = block.row, block.col
        if row in range(self.count_rows) and col in range(self.count_cols):
            self.matrix[row][col] = block

    def check_correct_x_y(self, x: float | int, y: float | int):
        row, col = x // const.SIZE_BLOCK, y // const.SIZE_BLOCK
        if self.check_correct_row_col(row, col):
            return True
        return False

    def draw(self, screen):
        self.group_room.draw(screen)

    def check_correct_row_col(self, row: int, col: int):
        if row in range(self.count_rows) and col in range(self.count_cols):
            return True
        return False

    def get_block_by_row_col(self, row: int, col: int):
        return self.matrix[row][col]

    def get_block_by_x_y(self, x: float | int, y: float | int):
        row, col = x // const.SIZE_BLOCK, y // const.SIZE_BLOCK
        return self.matrix[row][col]


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
            self.check_correction_coord(row_current_room, col_current_room) and
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
        self.speed = speed_move
        self.name = name
        self.hp = hp
        self.size_entity = size_entity
        if not (self.size_entity % const.SIZE_BLOCK):
            self.size_entity -= 2
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

    def move(self, room: Room, direction: tuple[int, int]):
        """Перемещение игрока."""
        # новый хитбокс
        x_direction, y_direction = direction
        k_x = x_direction * self.speed
        k_y = y_direction * self.speed
        new_hitbox = self.rect.move(k_x, k_y)
        borders_current_rect = {
            (0, -1): self.rect.top,
            (0, 1): self.rect.bottom,
            (-1, 0): self.rect.left,
            (1, 0): self.rect.right
        }
        borders_new_rect = {
            (0, -1): new_hitbox.top,
            (0, 1): new_hitbox.bottom,
            (-1, 0): new_hitbox.left,
            (1, 0): new_hitbox.right
        }
        border_current_rect_towards = borders_current_rect[direction]
        border_new_rect_towards = borders_new_rect[direction]
        if border_new_rect_towards < 0:
            border_new_rect_towards = 0
        elif border_new_rect_towards >= (
                border_room := room.width if direction[0] else room.height
        ):
            border_new_rect_towards = border_room - 1
        border_left = borders_current_rect[tuple(reversed(direction))]
        border_right = borders_current_rect[
            tuple(map(lambda x: -x, reversed(direction)))
        ]
        flag_break = False
        block = None
        begin_current = border_current_rect_towards // const.SIZE_BLOCK
        end_new = border_new_rect_towards // const.SIZE_BLOCK
        step_border_towards = 1 if end_new >= begin_current else -1
        begin_left = border_left // const.SIZE_BLOCK
        end_right = border_right // const.SIZE_BLOCK
        step_borders = 1 if end_right >= begin_left else -1
        for i in range(
                begin_current,
                end_new + step_border_towards,
                step_border_towards
        ):

            for j in range(
                    begin_left,
                    end_right + step_borders,
                    step_borders
            ):
                coord = (i, j) if direction[1] else (j, i)
                if room.get_block_by_row_col(
                        *coord).type_block == const.TYPE_BLOCK_WALL:
                    block = room.get_block_by_row_col(*coord)
                    flag_break = True
                    break
            if flag_break:
                break
        if block is not None:
            borders_block = {
                (0, -1): block.rect.top,
                (0, 1): block.rect.bottom,
                (-1, 0): block.rect.left,
                (1, 0): block.rect.right
            }
            border_block = borders_block[
                tuple(map(lambda x: -x, direction))
            ]
            distance = border_block - border_current_rect_towards - (
                direction[0] if direction[0] else direction[1]
            )
            if direction[0]:
                k_x = distance
            elif direction[1]:
                k_y = distance
        self.rect.move_ip(k_x, k_y)


def load_image(name: str, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
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
    container = GroupContainer()
    level = Level(3, 3)
    for i in range(3):
        for j in range(3):
            room = Room(random.randint(5, 10), random.randint(5, 10))
            level.set_room(room, i, j)
    level.set_current_room(0, 0)
    clock = pygame.time.Clock()
    running = True
    speed_player = {
        'UP': (0, -1),
        'DOWN': (0, 1),
        'LEFT': (-1, 0),
        'RIGHT': (1, 0)

    }
    image_hero = load_image('hero.png', -1)
    player_group = SpritesGroup()
    player = Player(
        250, 250, const.SIZE_PLAYER, image_hero, const.SPEED_PLAYER,
        100, 'qwerty', player_group
    )
    container.add_group(player, player_group)
    data = {
        pygame.K_w: (-1, 0),
        pygame.K_a: (0, -1),
        pygame.K_s: (1, 0),
        pygame.K_d: (0, 1),
    }
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and
                event.key == pygame.K_ESCAPE
            ):
                running = False
            if event.type == pygame.KEYDOWN:
                button = event.key
                if button in data:
                    if level.displace_current_room(*data[button]):
                        player.set_position(const.SIZE_BLOCK / 2 * 3,
                                            const.SIZE_BLOCK / 2 * 3)
        keys = pygame.key.get_pressed()
        room = level.get_current_room()
        if keys[pygame.K_UP]:
            player_group.update(room, speed_player['UP'])
        if keys[pygame.K_DOWN]:
            player_group.update(room, speed_player['DOWN'])
        if keys[pygame.K_LEFT]:
            player_group.update(room, speed_player['LEFT'])
        if keys[pygame.K_RIGHT]:
            player_group.update(room, speed_player['RIGHT'])
        current_room_blocks = level.get_current_room()
        room_screen = pygame.Surface((current_room_blocks.width,
                                      current_room_blocks.height))
        main_screen.fill('black')
        room_screen.fill('black')
        container.draw_group(room_screen, current_room_blocks)
        player_group.draw(room_screen)
        main_screen.blit(
            room_screen, (0, 0),
            player.get_screen_player(*main_screen.get_size())
        )
        pygame.display.flip()
        clock.tick(const.FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
