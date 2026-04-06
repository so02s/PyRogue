from __future__ import annotations
from Domain.items import Item
from typing import Any, Optional
from Controller.sound_controller import sounds

class Weapon(Item):
    type = "weapon"
    symbol = "†"
    color = 4
    
    _variants = {
        "Короткий меч": {"value": 30, "weight": 40},
        "Шипастая палица": {"value": 40, "weight": 24},
        "Булава": {"value": 50, "weight": 10},
        "Алебарда": {"value": 60, "weight": 5},
        "Глефа": {"value": 70, "weight": 4},
        "Копьё": {"value": 80, "weight": 4},
        "Двуручный меч": {"value": 100, "weight": 4},
        "Молот Войны": {"value": 150, "weight": 1},
    }

    def __init__(self, name: str):
        super().__init__(name)
        self.value = self._variants[name]["value"]
    
    @property
    def name(self):
        """
        Возвращает название с указанием силы
        """
        return f"{self._base_name} (+{self.value}% ATTACK)"
    
    def use(self, target: Any) -> Optional[Weapon]:
        sounds.use_weapon.play()
        old_weapon = target.add_weapon(self)
        return old_weapon

    def pick_up(self):
        sounds.add_weapon.play()

    def drop():
        pass
