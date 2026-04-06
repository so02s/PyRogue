from .door import DoorColor
from Domain.items import Item
from Controller.sound_controller import sounds

class Key(Item):
    type = "key"
    symbol = "⚷"

    def __init__(self, color: DoorColor):
        self.color_code = color
        self.color = self.color_code.value

    @property
    def name(self) -> str:
        return f"{self.color_code.name}"
    
    def pick_up(self):
        sounds.add_key.play()