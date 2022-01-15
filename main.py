import os

from entitys import Mob, Player, NPC
from levels import Room
from interfaces.templates import *
from level_generation import Generator
from items import RandomizerItems


class SpritesGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.disabled = False

    def update(self, *args, **kwargs):
        if not self.disabled:
            for sprite in self.sprites():
                sprite.update(*args, **kwargs)

    def clear_all(self):
        for sprite in self.sprites():
            sprite.kill()

    def set_new_room(self, room: Room):
        for sprite in self.sprites():
            sprite.room = room


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


class Game:
    def __init__(self):
        self.main_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.game_over = False
        self.stop_game = False
        self.main_interface = Interface(
            self.main_screen.get_size(), 10, 10
        )
        self.battle_interface = Interface(
            self.main_screen.get_size(), 20, 20
        )
        self.level = Level(10, 10)
        self.generator = Generator(10, 10)
        self.randomizer = RandomizerItems('data_base.sqlite')
        self.level.set_matrix(self.generator.generate(), (0, 0))
        self.__cycle()

    def __cycle(self):
        player_screen = pygame.Surface(self.main_screen.get_size())
        room = self.level.get_current_room()
        group1 = SpritesGroup()
        group2 = SpritesGroup()
        map_room = room.get_map()
        player = Player(map_room.get_object_by_name('player'), room,
                        group1)
        player.current_weapon = self.randomizer.get_item()
        InterfaceStartGame(self.main_interface, self.main_screen)
        InterfacePlayer(self.main_interface, player)
        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(const.FPS) / 1000
            room = self.level.get_current_room()
            group2.clear_all()
            for i in room.get_map().objects:
                if i.type == 'player':
                    continue
                if i.type == 'teleport':
                    NPC(i, room, group2)
                else:
                    mob = Mob(i, room, group2)
                    mob.current_weapon = self.randomizer.get_item()
            group1.set_new_room(room)
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
                    group1.update(player)
                    group2.update(player, self)
                self.main_interface.event_elements(event)
                self.battle_interface.event_elements(event)

            self.main_screen.fill('black')
            player_screen.fill('black')
            room.draw(player_screen)
            group1.draw(player_screen)
            group2.draw(player_screen)
            self.main_interface.update(time_delta)
            self.battle_interface.update(time_delta)

            self.main_screen.blit(
                player_screen, (0, 0), player.get_screen_player(
                    *player_screen.get_size()
                )
            )
            self.main_interface.draw_ui(self.main_screen)
            self.battle_interface.draw_ui(self.main_screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == '__main__':
    pygame.init()
    Game()
