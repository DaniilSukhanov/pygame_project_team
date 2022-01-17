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


class Game:
    def __init__(self):
        self.main_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.game_over = False
        self.stop_game = False
        self.state = 'start'
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
        self.count_kills = 0
        self.__cycle()

    def __cycle(self):

        clock = pygame.time.Clock()
        running = True
        while running:
            time_delta = clock.tick(const.FPS) / 1000
            if self.state == 'start':
                self.count_kills = 0
                InterfaceStartGame(self.main_interface, self.main_screen)
                self.level = Level(10, 10)
                self.level.set_matrix(self.generator.generate(), (0, 0))
                player_screen = pygame.Surface(self.main_screen.get_size())
                room = self.level.get_current_room()
                group_player = SpritesGroup()
                group_mob = SpritesGroup()
                group_npc = SpritesGroup()
                player = Player(room.get_map().get_object_by_name('player'), room,
                                group_player)
                player.current_weapon = self.randomizer.get_item()
                self.interface_player = InterfacePlayer(self.main_interface, player)
                self.state = 'game'
                continue
            if self.state == 'game' and player.current_health <= 0:
                self.state = 'game_over'
                continue
            if self.state == 'game_over':
                InterfaceGameOver(self.main_interface, self)
                self.state = 'start'
                continue
            room = self.level.get_current_room()
            group_mob.clear_all()
            group_npc.clear_all()
            for i in room.get_map().objects:
                if i.type == 'player':
                    continue
                if i.type == 'teleport':
                    NPC(i, room, group_npc).interface = InterfaceTeleport
                elif i.type == 'shop':
                    NPC(i, room, group_npc).interface = InterfaceShop
                else:
                    mob = Mob(i, room, group_mob)
                    mob.current_weapon = self.randomizer.get_item()
            group_player.set_new_room(room)
            group_npc.set_new_room(room)
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
                    group_player.update(player)
                    group_mob.update(player, self)
                    group_npc.update(player, self)
                self.main_interface.event_elements(event)
                self.battle_interface.event_elements(event)

            self.main_screen.fill('black')
            player_screen.fill('black')
            room.draw(player_screen)
            group_player.draw(player_screen)
            group_mob.draw(player_screen)
            group_npc.draw(player_screen)
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
