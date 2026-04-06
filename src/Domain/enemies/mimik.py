from .enemy import Enemy
from Domain.items import create_rnd_item
from Controller.sound_controller import sounds

class Mimic(Enemy):
    def __init__(self, level, actual_symb = None, actual_color = None):
        super().__init__('m', level)
        if actual_symb is None or actual_color is None:
            self.actual_symb = self.symbol
            self.actual_color = self.color

        else:
            self.actual_symb = actual_symb
            self.actual_color = actual_color
            
        fake_item = create_rnd_item(level)
        self.symbol = fake_item.symbol
        self.color = fake_item.color

    def _set_engaged_status(self) -> None:
        """
        Изменяет символ и цвет на настоящие
        """
        self.color = self.actual_color
        self.symbol = self.actual_symb
        super()._set_engaged_status()
    
    def hurt(self, points):
        sounds.hit_s.play()
        return super().hurt(points)