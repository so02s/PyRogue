from Domain.items import Item
from Domain.stat_util import StatType
from typing import Any
from Controller.sound_controller import sounds

class Potion(Item):
    type = "potion"
    symbol = "ⵒ"
    color = 2

    _variants = {
        "Зелье Прыткости": {"weight": 29, "effect": StatType.DEXTERITY, "value": 5, "duration": 15},
        "Зелье Мощи": {"weight": 21, "effect": StatType.STRENGTH, "value": 5, "duration": 15},
        "Зелье Тела": {"weight": 50, "effect": StatType.HEALTH, "value": 10, "duration": 30}
    }

    def __init__(self, name: str):
        super().__init__(name)
        data = self._variants[name]
        self.weight = data["weight"]
        self.effect_type = data["effect"]
        self.value = data["value"]
        self.duration = data["duration"]

    @property
    def name(self):
        """
        Возвращает название с указанием силы
        """
        return f"{self._base_name} (+{self.value} STEP)"

    def use(self, target: Any):
        sounds.use_potion.play()
        target.add_effect(self.effect_type, self.value, self.duration)

    def pick_up(self):
        sounds.add_potion.play()

    def drop():
        pass