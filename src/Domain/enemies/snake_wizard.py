from .enemy import Enemy
from random import random
from Controller.sound_controller import sounds

class SnakeWizard(Enemy):
    def __init__(self, level):
        super().__init__('s', level)
        
    def on_hit_player(self, player) -> int:
        if random() < 0.3:
            player.is_sleep = True
        return super().on_hit_player(player)
    
    def hurt(self, points):
        sounds.hit_s.play()
        return super().hurt(points)