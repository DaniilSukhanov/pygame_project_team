import pygame
import pygame_gui
from interfaces.elements import *
from entitys import Player, Mob
import const
from levels import Level


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
        self.player.update_property(room.get_map().get_object_by_name('player'), room, *self.player.groups())


class InterfacePlayer:
    def __init__(self, manager: Interface, player):
        self.hp_bar = InterfaceScreenSpaceHealthBar(
            (0, 0),
            (1, 3),
            manager,
            sprite_to_monitor=player
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
            (15, 15),
            manager
        )
        self.hp_bar_mob = InterfaceScreenSpaceHealthBar(
            (0, 0),
            (1, 2),
            manager,
            sprite_to_monitor=mob,
            container=self.window
        )
        self.button_attack = InterfaceButton(
            (1, 0),
            (1, 1),
            manager,
            text='Attack',
            container=self.window
        )
        self.button_attack.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            lambda _: self.attack(mob, player)
        )

    def attack(self, recipient: Player | Mob, sender: Player | Mob):
        recipient.current_health -= sender.current_weapon.damage
        if recipient.current_health <= 0:
            self.window.kill()
            recipient.kill()
            self.game.stop_game = False
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
    def __init__(self, manager):
        self.panel = InterfacePanel(
            (0, 0),
            (20, 20),
            manager
        )
        self.label = InterfaceLabel(
            (10, 8),
            (10, 12),
            manager,
            container=self.panel
        )



