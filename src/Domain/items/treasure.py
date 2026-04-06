from Domain.items import Item
from typing import Any
from Controller.sound_controller import sounds

class Treasure(Item):
    type = "сокровище"
    symbol = "◈"
    color = 18

    def __init__(self, name, value: int):
        super().__init__(name)
        self.value = value
    
    def use(self):
        pass

    def pick_up(self, target: Any):
        sounds.add_gold.play()
        target.add_gold(self.value)

    def drop():
        pass