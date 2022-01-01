import pygame

from pygame_gui.elements import *
from interfaces.interface import Interface
from pygame_gui.core import UIElement


class InterfaceElement:
    def add_function(
            self: UIElement,
            user_type_event: int,
            function
    ):
        """Добавляет функцию,
         которая срабатывает при определенных обстоятельствах."""
        self.ui_manager.add_element_function(
            self,
            user_type_event,
            function
        )

    def set_position(
            self: UIElement,
            position: tuple[float | int] | list[float | int]
    ):
        """Меняет позицию элемента (позиция указывается как строкаБ столбец)"""
        size_cell = self.ui_manager.size_cell
        UIElement.set_position(
            self,
            (
                position[0] * size_cell[0],
                position[1] * size_cell[1]
            )
        )


class InterfaceButton(InterfaceElement, UIButton):
    def __init__(
            self,
            position: tuple[int | float, int | float] | list[float | int],
            size: tuple[int | float, int | float] | list[float | int],
            manager: Interface,
            text: str = '',
            **kwargs
    ):
        super().__init__(
            relative_rect=create_rect(
                position,
                size,
                manager
            ),
            manager=manager,
            text=text,
            **kwargs
        )


class InterfaceLabel(InterfaceElement, UILabel):
    def __init__(
            self,
            position: tuple[int | float, int | float] | list[float | int],
            size: tuple[int | float, int | float] | list[float | int],
            manager: Interface,
            text: str = '',
            **kwargs
    ):
        super().__init__(
            manager=manager,
            text=text,
            relative_rect=create_rect(position, size, manager),
            **kwargs
        )


class InterfaceDropDownMenu(InterfaceElement, UIDropDownMenu):
    def __init__(
            self,
            position: tuple[int | float, int | float] | list[float | int],
            size: tuple[int | float, int | float] | list[float | int],
            manager: Interface,
            options_list: list[str],
            starting_option: str,
            **kwargs
    ):
        super().__init__(
            relative_rect=create_rect(position, size, manager),
            manager=manager,
            options_list=options_list,
            starting_option=starting_option,
            **kwargs
        )


class InterfaceWindow(InterfaceElement, UIWindow):
    def __init__(
            self,
            position: tuple[int | float, int | float] | list[float | int],
            size: tuple[int | float, int | float] | list[float | int],
            manager: Interface,
            **kwargs
    ):
        super().__init__(
            rect=create_rect(position, size, manager),
            manager=manager,
            **kwargs
        )


class InterfaceScreenSpaceHealthBar(InterfaceElement, UIScreenSpaceHealthBar):
    def __init__(
            self,
            position: tuple[int | float, int | float] | list[float | int],
            size: tuple[int | float, int | float] | list[float | int],
            manager: Interface,
            **kwargs
    ):
        super().__init__(
            relative_rect=create_rect(position, size, manager),
            manager=manager,
            **kwargs
        )


def create_rect(
        position: tuple[int | float, int | float] | list[float | int],
        size: tuple[int | float, int | float] | list[float | int],
        manager: Interface
) -> pygame.Rect:
    size_cell = manager.size_cell
    return pygame.Rect(
        (
            size_cell[0] * position[0],
            size_cell[1] * position[1]
        ),
        (
            size_cell[0] * size[0],
            size_cell[1] * size[1]
        )
    )
