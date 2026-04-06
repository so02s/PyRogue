from .enemy import Enemy
from Controller.sound_controller import sounds

class Ork(Enemy):
    def __init__(self, level):
        super().__init__('O', level)
        self.resting = True

    def hit_player(self, player_dex: int) -> bool:
        """
        Либо отдыхает, либо попадает
        """
        self.resting = not self.resting
        return not self.resting
    
    def hurt(self, points):
        sounds.hit_o.play()
        return super().hurt(points)