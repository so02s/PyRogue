from .singletone_wrapper import SingletonMeta
from Domain import Coordinate
from Domain.items.weapon import Weapon
from Controller.sound_controller import sounds
from .stat_util import StatType, Direction
from typing import Optional

class _Character(metaclass=SingletonMeta):
    symbol = '@'

    def __init__(self, x: int = 0, y: int = 0, base: int = 50, direction: Direction = Direction.RIGHT) -> None:
        """
        x, y - координаты
        """
        self._effects = {}
        self.base_strength: int = 10
        self.base_dexterity: int = 10
        self.base_health: int = base
        self.current_health: int = self.maximum_health
        self.x, self.y = x, y
        self.skill_lvl: float = 0.5
        self.weapon: Weapon = None
        self.is_sleep: bool = False
        self.direction = direction
        
    @property
    def color(self) -> int:
        return 6 if self.is_sleep else 7

    @property
    def strength(self) -> int:
        base = self.base_strength
        if StatType.STRENGTH in self._effects:
            base += self._effects[StatType.STRENGTH][0]
        return base

    @strength.setter
    def strength(self, value: int):
        self.base_strength = value

    @property
    def dexterity(self) -> int:

        if self.is_sleep:
            return 0
        base = self.base_dexterity
        if StatType.DEXTERITY in self._effects:
            base += self._effects[StatType.DEXTERITY][0]
        return base
    
    @dexterity.setter
    def dexterity(self, value: int):
        self.base_dexterity = value
    
    @property
    def maximum_health(self) -> int:
        base = self.base_health
        if StatType.HEALTH in self._effects:
            base += self._effects[StatType.HEALTH][0]
        return base

    def add_effect(self, effect_type: int, value: int, duration: int) -> None:
        """
        Добавляет эффект с указанной длительностью
        """
        self._effects[effect_type] = (value, duration)
        if effect_type == StatType.HEALTH:
            self.current_health += value

    def tick_effects(self) -> None:
        """
        Уменьшает длительность эффектов на 1 ход, удаляет истёкшие
        """
        expired = []
        for effect, (val, dur) in self._effects.items():
            if dur <= 1:
                expired.append(effect)
            else:
                self._effects[effect] = (val, dur - 1)
        for e in expired:
            if e == StatType.HEALTH and self.base_health < 0:
                self.base_health = 1
            del self._effects[e]

    def restart(self) -> None:
        """
        Перегенерация персонажа
        """
        self.base_strength = 10
        self.base_dexterity = 10
        self.base_health = 50
        self.current_health = self.maximum_health
        self.weapon = None
        self._effects.clear()
    

    def set_crd(self, crd: Coordinate) -> None:
        """
        Установить коорднату
        """
        self.y, self.x = crd

    @property
    def crd(self) -> Coordinate:
        """
        Вернуть координату
        """
        return (self.y, self.x)

    def attack(self) -> int:
        """
        Сколько урона нанесет персонаж
        """
        base = self.strength
        if self.weapon:
            multiplier = 1 + self.weapon.value / 100
            return int(base * multiplier)
        return base
    
    def move(self, crd: Coordinate) -> None:
        """
        Переместить на столько
        """
        self.x += crd[1]
        self.y += crd[0]

    def heal(self, points: int) -> None:
        """
        Вылечить на столько поинтов
        """
        self.current_health += points
        if self.current_health > self.maximum_health:
            self.current_health = self.maximum_health

    def hurt(self, points: int) -> None:
        """
        Урон по персонажу
        """
        if points:
            sounds.hit_c.play()
            self.current_health -= points
    
    def add_statistic(self, stat_type: int, points: int) -> None:
        """
        Добавить характеристики
        """
        if stat_type == StatType.DEXTERITY:
            self.base_dexterity += points
        elif stat_type == StatType.STRENGTH:
            self.base_strength += points
        elif stat_type == StatType.HEALTH:
            self.base_health += points
            self.current_health += points
    
    def is_dead(self) -> bool:
        """
        Мертв ли персонаж
        """
        if self.current_health <= 0:
            return True
        return False
    
    def now_weapon(self) -> Optional[str]:
        """
        Возвращает строку - нынешнее оружие
        """
        return self.weapon.name.capitalize() if self.weapon else "-"
    
    def add_weapon(self, new_weapon: Optional[Weapon]) -> Optional[Weapon]:
        """
        Меняет старое на новое оружие, возвращает старое
        """
        old_weapon = self.weapon
        self.weapon = new_weapon
        return old_weapon
    
    def direction_left(self) -> None:
        """
        Повернуть вид налево
        """
        mapping = {
            Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
            Direction.UP: Direction.RIGHT,
        }
        self.direction = mapping[self.direction]

    def direction_right(self) -> None:
        """
        Повернуть вид направо
        """
        mapping = {
            Direction.RIGHT: Direction.UP,
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN,
            Direction.DOWN: Direction.RIGHT,
        }
        self.direction = mapping[self.direction]

player = _Character()