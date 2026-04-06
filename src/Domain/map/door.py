from enum import Enum

class DoorColor(Enum):
    RED = 2
    BLUE = 7
    YELLOW = 6

class Door():
    type = "door"

    def __init__(self, color: DoorColor, room_a: int = None, room_b: int = None, locked: bool = True):
        self.color_code = color
        self.color = self.color_code.value
        self.symbol = "█"
        self.locked = locked

        self.room_a = room_a
        self.room_b = room_b