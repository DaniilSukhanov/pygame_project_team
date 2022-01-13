import pygame
import pygame_gui
from interfaces.elements import *
from entitys import Player, Mob
import const


class InterfaceTeleport:
    def __init__(self, manager: Interface):
        self.button = InterfaceButton(
            (1, 1),
            (1, 1),
            manager
        )
        self.button.add_function(
            pygame_gui.UI_BUTTON_PRESSED,
            self.__press
        )

    @staticmethod
    def __press(interface_element):
        print(123)


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

    @staticmethod
    def attack(recipient: Player | Mob, sender: Player | Mob):
        recipient.current_health -= 1


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



