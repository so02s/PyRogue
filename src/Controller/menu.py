from Domain import SingletonMeta
from .states import GameStates

class _Menu(metaclass=SingletonMeta):
    
    def __init__(self):
        self.selected_index: int = 0
        self._active_game_items = [
            ("Continue", GameStates.GAME),
            ("Start new game", GameStates.NEW_GAME),
            ("Statistica", GameStates.STATISTICA),
            ("Settings", GameStates.SETTINGS),
            ("Exit", GameStates.EXIT),
        ]
        self._inactive_game_items = [
            ("Start new game", GameStates.NEW_GAME),
            ("Load last game", GameStates.LOAD_GAME),
            ("Statistica", GameStates.STATISTICA),
            ("Settings", GameStates.SETTINGS),
            ("Exit", GameStates.EXIT),
        ]
        self.menu_items = self._inactive_game_items[:]
    
    def set_active_game(self, active: bool = True):
        self.menu_items = self._active_game_items[:] if active else self._inactive_game_items[:]
        if self.selected_index >= len(self.menu_items):
            self.selected_index = len(self.menu_items) - 1

    def reopen(self) -> None:
        self.selected_index = 0

    def length(self) -> int:
        return len(self.menu_items)
    
    def next(self) -> None:
        if self.selected_index < self.length() - 1:
            self.selected_index += 1
    
    def prev(self) -> None:
        if self.selected_index > 0:
            self.selected_index -= 1

    def use_command(self, controller) -> None:
        controller.state = self.menu_items[self.selected_index][1]
        
menu = _Menu()