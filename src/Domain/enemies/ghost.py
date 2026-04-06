from .enemy import Enemy
from random import random, randint
from Domain import Coordinate
from Controller.sound_controller import sounds

class Ghost(Enemy):
    def __init__(self, level: int):
        super().__init__('g', level)
        self.invisible_counter = 0
        self.invisible = False

    def _update_invisibility(self):
        """
        Периодическая смена видимости вне боя
        """
        if self.invisible_counter > 0:
            self.invisible_counter -= 1
            if self.invisible_counter == 0:
                self.invisible = False
                return

        if random() < 0.2:
            self.invisible = True
            self.invisible_counter = randint(3, 5)
    
    def _move_engaged(self, mob_crd: Coordinate, map) -> Coordinate:
        """
        Призрак виден когда заагрен
        """
        self.invisible = False
        return super()._move_engaged(mob_crd, map)
    
    def _move_by_pattern(self, mob_crd: Coordinate, map) -> Coordinate:
        """
        Периодически пропадает когда перемещается
        """
        self._update_invisibility()
        return super()._move_by_pattern(mob_crd, map)
    
    def hurt(self, points):
        sounds.hit_g.play()
        return super().hurt(points)