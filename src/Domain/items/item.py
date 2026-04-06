import random
from abc import ABC, abstractmethod
from typing import Any, Dict

class Item(ABC):
    type = 'item'
    symbol = '?'
    color = 1

    _variants: Dict[str, Dict[str, Any]] = {}

    def __init__(self, name: str) -> None:
        self._base_name = name

    @classmethod
    def random(cls, lvl: int):
        names = list(cls._variants.keys())
        weights = [cls._variants[name]["weight"] for name in names]
        chosen_name = random.choices(names, weights=weights)[0]
        return cls(chosen_name)
    
    @abstractmethod
    def pick_up():
        """Поднять предмет"""
        pass

    # @abstractmethod
    # def drop():
    #     """Вывод инфы о сброшенном предмете"""
    #     pass

    # @abstractmethod
    # def use(self):
    #     """Вывод инфы о использованном предмете"""
    #     pass
