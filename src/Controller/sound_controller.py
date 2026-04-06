import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pathlib import Path
from Domain import SingletonMeta

class _SoundController(metaclass=SingletonMeta):
    def __init__(self):
        pygame.init()
        sounds_dir = self._find_project_root() / "misc" / "sounds"

        self.intro = pygame.mixer.Sound(str(sounds_dir / "intro_2.ogg"))

        self.add_key = pygame.mixer.Sound(str(sounds_dir / "key_add.ogg"))
        self.add_food = pygame.mixer.Sound(str(sounds_dir / "add_food.ogg"))
        self.add_gold = pygame.mixer.Sound(str(sounds_dir / "add_gold.ogg"))
        self.add_weapon = pygame.mixer.Sound(str(sounds_dir / "add_weapon.ogg"))
        self.add_potion = pygame.mixer.Sound(str(sounds_dir / "potion_add.ogg"))
        self.add_scroll = pygame.mixer.Sound(str(sounds_dir / "scroll_add.ogg"))
        self.use_scroll = pygame.mixer.Sound(str(sounds_dir / "scroll_use.ogg"))
        self.use_food = pygame.mixer.Sound(str(sounds_dir / "use_food.ogg"))
        self.use_weapon = pygame.mixer.Sound(str(sounds_dir / "use_weapon.ogg"))
        self.use_potion = pygame.mixer.Sound(str(sounds_dir / "potion_use.ogg"))

        self.hit_c = pygame.mixer.Sound(str(sounds_dir / "hit_character.ogg"))

        self.miss_sound = pygame.mixer.Sound(str(sounds_dir / "miss_sound.ogg"))
        self.enemy_engaged = pygame.mixer.Sound(str(sounds_dir / "enemy_engaged.ogg"))
        self.hit_g = pygame.mixer.Sound(str(sounds_dir / "hit_ghost.ogg"))
        self.hit_o = pygame.mixer.Sound(str(sounds_dir / "hit_ogre.ogg"))
        self.hit_s = pygame.mixer.Sound(str(sounds_dir / "hit_snake_mage.ogg"))
        self.hit_v = pygame.mixer.Sound(str(sounds_dir / "hit_vampire.ogg"))
        self.hit_z = pygame.mixer.Sound(str(sounds_dir / "hit_zombie.ogg"))

        self.door_open = pygame.mixer.Sound(str(sounds_dir / "door_open.ogg"))
        self.next_level = pygame.mixer.Sound(str(sounds_dir / "next_level.ogg"))
        
        self.win = pygame.mixer.Sound(str(sounds_dir / "win.ogg"))
        self.gameover = pygame.mixer.Sound(str(sounds_dir / "gameover.ogg"))
    
    @staticmethod
    def _find_project_root(marker ="misc"):
        current  = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / marker).exists():
                return parent
        return Path.cwd()


sounds = _SoundController()