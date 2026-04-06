from Domain.items import Item
from Controller.sound_controller import sounds

class Food(Item):
    type = "food"
    symbol = "ⴻ"
    color = 1

    _variants = {
        "Яблоко": {"value": 10, "weight": 50},
        "Манго": {"value": 30, "weight": 40},
        "Хлеб": {"value": 50, "weight": 20},
        "Кроличье рагу": {"value": 100, "weight": 15},
        "Эликсир Жизни": {"value": 1000, "weight": 2},
    }

    def __init__(self, name: str):
        super().__init__(name)
        self.value = self._variants[name]["value"]
    
    @property
    def name(self):
        """
        Возвращает название с кол-ва хп
        """
        return f"{self._base_name} (+{self.value} HP)"

    def use(self, target) -> None:
        sounds.use_food.play()
        target.heal(self.value)

    def pick_up(self):
        sounds.add_food.play()

    def drop():
        pass