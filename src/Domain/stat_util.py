from enum import Enum

class StatType(Enum):
    DEXTERITY = 1
    STRENGTH = 2
    HEALTH = 3

class Direction(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3