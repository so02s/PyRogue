from .enemy import Enemy
from Controller.sound_controller import sounds

class Zombie(Enemy):
    def __init__(self, level):
        super().__init__('z', level)
    
    def hurt(self, points):
        sounds.hit_z.play()
        return super().hurt(points)