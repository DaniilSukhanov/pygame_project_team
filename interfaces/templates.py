import pygame
import pygame_gui
from interfaces.elements import *
from entitys import Player, Mob
import const
import random
from levels import Level
from load_image import load_image
from items import RandomizerItems


class InterfaceTeleport:
    def __init__(self, manager: Interface, game, player: Player):
        self.level = game.level
        self.game = game
        game.stop_game = True
        self.player = player
        self.window = InterfaceWindow(
            (0, 0),
            (10, 10),
            manager
        )
        self.button_up = InterfaceButton(
            (0, 1),
            (1, 1),
            manager,
            text='UP',
            container=self.window
        )
        self.button_up.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.press(-1, 0)
        )
        self.button_down = InterfaceButton(
            (1, 1),
            (1, 1),
            manager,
            text='DOWN',
            container=self.window
        )
        self.button_down.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.press(1, 0)
        )
        self.button_left = InterfaceButton(
            (1, 0),
            (1, 1),
            manager,
            text='LEFT',
            container=self.window
        )
        self.button_left.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.press(0, -1)
        )
        self.button_right = InterfaceButton(
            (1, 2),
            (1, 1),
            manager,
            text='RIGHT',
            container=self.window
        )
        self.button_right.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.press(0, 1)
        )

    def press(self, k_row, k_col):
        self.level.displace_current_room(k_row, k_col)
        room = self.level.get_current_room()
        weapon = self.player.current_weapon
        self.player.update_property(room.get_map().get_object_by_name('player'), room, *self.player.groups())
        self.player.current_weapon = weapon


class InterfacePlayer:
    def __init__(self, manager: Interface, player):
        self.hp_bar = InterfaceScreenSpaceHealthBar(
            (0, 0),
            (1, 3),
            manager,
            sprite_to_monitor=player
        )
        self.image_coin = InterfaceImage(
            (0, 9),
            (1, 1),
            manager,
            load_image('coin.png', -1)
        )
        self.count_coin = InterfaceLabel(
            (1, 9),
            (1, 1),
            manager,
            '0'
        )


class InterfaceBattle:
    def __init__(
            self,
            manager: Interface,
            game,
            player: Player,
            mob: Mob
    ):
        self.game = game
        self.game.stop_game = True
        self.window = InterfaceWindow(
            (2, 1),
            (10, 4.5),
            manager
        )
        self.hp_bar_mob = InterfaceScreenSpaceHealthBar(
            (0, 0),
            (1, 4),
            manager,
            sprite_to_monitor=mob,
            container=self.window
        )
        self.button_attack = InterfaceButton(
            (1, 0),
            (1, 4),
            manager,
            text='Attack',
            container=self.window
        )
        self.button_attack.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.attack(mob, player)
        )
        self.panel_mob_weapon = InterfacePanel(
            (2, 0),
            (6, 2),
            manager,
            container=self.window
        )
        self.image_mob_weapon = InterfaceImage(
            (0, 0),
            (3, 2),
            manager,
            mob.current_weapon.image,
            container=self.panel_mob_weapon
        )
        self.label_mob = InterfaceLabel(
            (3, 0),
            (1, 2),
            manager,
            'Оружие монстра:',
            container=self.panel_mob_weapon
        )
        self.label_mob_weapon = InterfaceLabel(
            (4, 0),
            (1, 2),
            manager,
            mob.current_weapon.name,
            container=self.panel_mob_weapon
        )
        self.label_mob_damage = InterfaceLabel(
            (5, 0),
            (1, 2),
            manager,
            f'Урон: {mob.current_weapon.damage}',
            container=self.panel_mob_weapon
        )
        self.panel_player_weapon = InterfacePanel(
            (2, 2),
            (6, 2),
            manager,
            container=self.window
        )
        self.image_player_weapon = InterfaceImage(
            (0, 0),
            (3, 2),
            manager,
            player.current_weapon.image,
            container=self.panel_player_weapon
        )
        self.label_player = InterfaceLabel(
            (3, 0),
            (1, 2),
            manager,
            'Ваше оружие:',
            container=self.panel_player_weapon
        )
        self.label_player_weapon = InterfaceLabel(
            (4, 0),
            (1, 2),
            manager,
            player.current_weapon.name,
            container=self.panel_player_weapon
        )
        self.label_player_damage = InterfaceLabel(
            (5, 0),
            (1, 2),
            manager,
            f'Урон: {player.current_weapon.damage}',
            container=self.panel_player_weapon
        )
        self.window.close_window_button.kill()

    def attack(self, recipient: Player | Mob, sender: Player | Mob):
        recipient.current_health -= sender.current_weapon.damage
        if recipient.current_health <= 0:
            self.window.kill()
            recipient.kill()
            self.game.stop_game = False
            if type(sender) == Player:
                self.game.count_kills += 1
                sender.money += random.randint(1, 10)
                self.game.interface_player.count_coin.set_text(str(sender.money))
        if type(recipient) == Mob:
            self.attack(sender, recipient)


class InterfaceStartGame:
    def __init__(self, manager: Interface, screen: pygame.Surface):
        self.panel = InterfacePanel(
            (0, 0),
            (10, 10),
            manager
        )
        self.running = True
        self.button = InterfaceButton(
            (4, 4),
            (1, 1),
            manager,
            text='Start Game',
            container=self.panel
        )
        self.button.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            self.clock
        )
        clock = pygame.time.Clock()
        while self.running:
            time_delta = clock.tick(const.FPS) / 1000
            for event in pygame.event.get():
                manager.event_elements(event)
            manager.update(time_delta)
            manager.draw_ui(screen)
            pygame.display.flip()
        manager.clear_and_reset()

    def clock(self, _):
        self.running = False


class InterfaceGameOver:
    def __init__(self, manager, game):
        self.game = game
        self.panel = InterfacePanel(
            (0, 0),
            (10, 10),
            manager
        )
        self.label = InterfaceLabel(
            (4, 4),
            (1, 1),
            manager,
            text=f'Убито: {game.count_kills}',
            container=self.panel
        )
        self.button = InterfaceButton(
            (5, 4),
            (1, 1),
            manager,
            text='Далее',
            container=self.panel
        )
        self.button.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            self.press
        )
        self.running = True
        clock = pygame.time.Clock()
        while self.running:
            time_delta = clock.tick(const.FPS) / 1000
            for event in pygame.event.get():
                manager.event_elements(event)
            manager.update(time_delta)
            manager.draw_ui(self.game.main_screen)
            pygame.display.flip()
        manager.clear_and_reset()

    def press(self, _):
        self.running = False


class InterfaceShop:
    def __init__(self, manager, game, player):
        self.window = InterfaceWindow(
            (0, 0),
            (5, 5),
            manager
        )
        self.game = game
        game.stop_game = True
        self.player = player
        randomizer = RandomizerItems('data_base.sqlite')
        items = tuple(
            map(
                lambda _: (randomizer.get_item(), random.randint(1, 10)),
                range(3)
            )
        )
        self.image_item1 = InterfaceImage(
            (0, 0),
            (1, 1),
            manager,
            items[0][0].image,
            container=self.window
        )
        self.price_item1 = InterfaceButton(
            (1, 0),
            (1, 1),
            manager,
            container=self.window,
            text=f'{items[0][1]}'
        )
        self.price_item1.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.buy_item(*items[0])
        )

        self.image_item2 = InterfaceImage(
            (0, 1),
            (1, 1),
            manager,
            items[1][0].image,
            container=self.window
        )
        self.price_item2 = InterfaceButton(
            (1, 1),
            (1, 1),
            manager,
            container=self.window,
            text=f'{items[1][1]}'
        )
        self.price_item2.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.buy_item(*items[1])
        )

        self.image_item3 = InterfaceImage(
            (0, 2),
            (1, 1),
            manager,
            items[2][0].image,
            container=self.window
        )
        self.price_item3 = InterfaceButton(
            (1, 2),
            (1, 1),
            manager,
            container=self.window,
            text=f'{items[2][1]}'
        )
        self.price_item3.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.buy_item(*items[2])
        )

    def buy_item(self, item, price):
        if self.player.money >= price:
            self.player.current_weapon = item
            self.player.money -= price





