from random import uniform, choice, random
from abc import ABC
from enum import Enum
from Domain import Coordinate, player
from Controller.sound_controller import sounds
from typing import Optional, List
from collections import deque

class MovePattern(Enum):
    STANDARD = 1
    DIAGONAL = 2
    JUMP = 3

class EnemyState(Enum):
    WALKING = 1
    ENGAGED = 2

class Enemy(ABC):
    _enamy_scale = 1.15
    _harm_color = 10

    # name color                    health dexterity speed strength hostility pattern
    _enemy_attr = {
        "z": ("Zombie", 8,          28, 5, 1, 5, 5, MovePattern.STANDARD),
        "v": ("Vampire", 9,         32, 9, 1, 4, 8, MovePattern.STANDARD),
        "g": ("Ghost", 5,           20, 10, 0, 2, 3, MovePattern.JUMP),
        "O": ("Ork", 6,             45, 4, 2, 10, 6, MovePattern.STANDARD),
        "s": ("Snake Wizard", 5,    25, 12, 1, 2, 10, MovePattern.DIAGONAL),
        "m": ("Mimik", 5,           30, 8, 0, 4, 1, MovePattern.STANDARD),
    }

    
    def __init__(self, type: str, level: int, health: float = None, dexterity: float = None, strength: float = None):
        self.symbol = type
        self.type = type
        (self.name, self.color, base_health, base_dexterity, self.speed,
         base_strength, self._hostility, self.pattern) = self._enemy_attr[type]
        
        self.health = health
        self.dexterity = dexterity
        self.strength = strength
    
        scale = pow(self._enamy_scale, level - 1)
        if health is None and dexterity is None and strength is None:
            self.health = self.__attr_randomize(base_health * scale)
            self.dexterity = self.__attr_randomize(base_dexterity * scale)
            self.strength = self.__attr_randomize(base_strength * scale)
        
        self.level = level
        self.state = EnemyState.WALKING
        self.is_visible = True

        self.engaged_sound = sounds.enemy_engaged
    
    def get_type(self) -> str:
        return self.symbol

    @staticmethod
    def __attr_randomize(value: int) -> int:
        """
        Рандом атрибутов
        """
        return max(3, round(value * uniform(0.8, 1.2)))

    def is_alive(self):
        """
        Жив ли моб
        """
        return self.health > 0

    def is_engaged(self) -> bool:
        """
        Заагрен ли моб
        """
        return self.state == EnemyState.ENGAGED

    def check_engaged(self, mob_crd: Coordinate, map) -> None:
        """
        Проверка видит ли игрока и установка агра, если видит
        """
        if self._BFS_to_player(mob_crd, map):
            self._set_engaged_status()
    
    def _set_engaged_status(self) -> None:
        """
        Поменять статус моба (про преследование)
        """
        if self.state != EnemyState.ENGAGED:
            self.engaged_sound.play()
            self.state = EnemyState.ENGAGED
    
    def hurt(self, points: int) -> None:
        """
        Урон по мобу
        """
        self.health -= points
    
    def next_move(self, mob_crd: Coordinate, map) -> Coordinate:
        """
        Возвращает следующую позицию врага
        """
        return self._move_engaged(mob_crd, map) if self.is_engaged() else self._move_by_pattern(mob_crd, map)
    
    def _move_by_pattern(self, mob_crd: Coordinate, map) -> Coordinate:
        """
        Движение по паттерну
        """
        if self.pattern == MovePattern.STANDARD:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        elif self.pattern == MovePattern.DIAGONAL:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        elif self.pattern == MovePattern.JUMP and random() < 0.3:
            room_id = map.get_room_id_by_crd(mob_crd)
            new_crd = map._get_rnd_free_crd(room_id)
            return new_crd if new_crd is not None else mob_crd
        else:
            return mob_crd

        candidates = [mob_crd]
        for dy, dx in directions:
            ny = mob_crd[0] + dy * self.speed
            nx = mob_crd[1] + dx * self.speed
            if map.is_walkable(ny, nx) and not map.is_door(ny, nx):
                candidates.append((ny, nx))
        return choice(candidates)

    def _move_engaged(self, mob_crd: Coordinate, map) -> Coordinate:
        tree = self._BFS_to_player(mob_crd, map)
        if tree is None:
            return mob_crd
        step = player.crd
        while tree[step] != mob_crd:
            step = tree[step]
        if step == player.crd:
            return mob_crd
        return step

    def _BFS_to_player(self, mob_crd: Coordinate, map) -> Optional[dict]:
        """
        Путь до игрока, если попадает в зону агра
        """
        start = mob_crd
        target = player.crd

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        parent = {start: None}
        dist = {start: 0}
        queue = deque([start])

        while queue:
            y, x = queue.popleft()
            current_dist = dist[(y, x)]

            if current_dist > self._hostility:
                continue

            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if not map.is_walkable(ny, nx) or map.is_door(ny, nx):
                    continue
                if (ny, nx) not in parent:
                    parent[(ny, nx)] = (y, x)
                    if (ny, nx) == target:
                        return parent
                    dist[(ny, nx)] = current_dist + 1
                    queue.append((ny, nx))
        return None
    
    def hit(self, player_dex: int) -> bool:
        """
        Попадание по мобу
        """
        chance = player_dex / (self.dexterity + player_dex)
        return random() < chance
        
    def hit_player(self, player_dex: int) -> bool:
        """
        Попадание мобом по игроку
        """
        chance = self.dexterity / (self.dexterity + player_dex)
        return random() < chance
    
    def on_hit_player(self, player) -> int:
        """
        Сколько урона наносит игроку
        """
        return self.strength