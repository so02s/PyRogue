from Domain.items import Item
from Domain.stat_util import StatType
from random import choices
from Controller.sound_controller import sounds

class Scroll(Item):
    type = "scroll"
    symbol = "ʃ"
    color = 4

    _variants = {
        "Свиток Прыткости": {"weight": 29, "stat_type": StatType.DEXTERITY},
        "Свиток Мощи": {"weight": 21, "stat_type": StatType.STRENGTH},
        "Свиток Тела": {"weight": 50, "stat_type": StatType.HEALTH}
    }

    def __init__(self, name: str, value: int):
        super().__init__(name)
        self.weight = self._variants[name]['weight']
        self.stat_type = self._variants[name]['stat_type']
        self.value = value

    @classmethod
    def random(cls, level: int = 1, skill_lvl: float = 0.5):
        names = list(cls._variants.keys())
        weights = [cls._variants[name]['weight'] for name in names]
        chosen_name = choices(names, weights=weights)[0]
        value = level * 3
        return cls(chosen_name, value)
    
    @property
    def name(self):
        """
        Возвращает название с указанием силы
        """
        return f"{self._base_name} (+{self.value})"
    
    def use(self, target):
        sounds.use_scroll.play()
        target.add_statistic(self.stat_type, self.value)

    def pick_up(self):
        sounds.add_scroll.play()

    def drop():
        pass
