import pygame_gui
from interfaces.elements import *


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
