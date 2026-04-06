from random import random
from .enemy import Enemy
from Controller.sound_controller import sounds

class Vampire(Enemy):
    def __init__(self, level, first_attack: bool = True):
        super().__init__('v', level)
        self.first_attack = first_attack

    def on_hit_player(self, player) -> int:
        """
        При успешной атаке уменьшает максимальное здоровье игрока
        """
        player.base_health -= self.strength
        if player.base_health < 1:
            player.base_health = 1
        if player.current_health > player.maximum_health:
            player.current_health = player.maximum_health
        return 0

    def hit_player(self, player_dex: int) -> bool:
        """
        Проверка попадания вампира. Первый удар всегда промах
        """
        if self.first_attack:
            self.first_attack = False
            return False
        chance = self.dexterity / (self.dexterity + player_dex)
        return random() < chance
    
    def hurt(self, points):
        sounds.hit_v.play()
        return super().hurt(points)