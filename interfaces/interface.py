import pygame
import pygame_gui


class Interface(pygame_gui.UIManager):
    def __init__(
            self,
            size_window: tuple[int, int] | list[int, int],
            count_rows: int,
            count_cols: int,
            *args, **kwargs
    ):
        super().__init__(size_window, *args, **kwargs)
        # Словарь, в котором ключами будут пользовательские события,
        # а значениями - словари, содержащие ключи - элемент диалога,
        # а значения ключей - список функций.
        self.elements = {}
        self.rows = count_rows
        self.cols = count_cols
        # размер клетки.
        self.size_cell = (
            size_window[0] / count_rows,
            size_window[1] / count_cols
        )
        self.disable = False

    def event_elements(
            self,
            event: pygame.event.Event,
            *args,
            **kwargs
    ):
        """Активация функций элемента. Возвращает словарь:
         ключ - функция, значения - результат функции."""
        self.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type in self.elements:
                ui_elements = self.elements[event.user_type]
                if event.ui_element in ui_elements:
                    function_ui_element = ui_elements[event.ui_element]
                    interface_element = set(
                        filter(
                            lambda element: element == event.ui_element,
                            ui_elements
                        )
                    ).pop()
                    function_ui_element(interface_element, *args, **kwargs)

    def add_element_function(
            self,
            element,
            user_type_event: int,
            function
    ):
        """Добавляет к элементу функцию."""
        if user_type_event not in self.elements:
            self.elements[user_type_event] = {element: function}
        elif element not in self.elements[user_type_event]:
            self.elements[user_type_event] |= {element: function}
        else:
            self.elements[user_type_event][element] = function

