from random import randint, choices
from .enemy import Enemy
from .zombie import Zombie
from .vampire import Vampire
from .ghost import Ghost
from .ork import Ork
from .snake_wizard import SnakeWizard
from .mimik import Mimic

_ENEMY_WEIGHTS = {
    Zombie: 30,
    Vampire: 15,
    Ghost: 20,
    Ork: 10,
    SnakeWizard: 15,
    Mimic: 10,
}

def create_rnd_enemy(lvl: int, skill_lvl: float) -> Enemy:
    variation = randint(-1, 1)
    if skill_lvl > 0.7:
        variation = randint(0, 2)
    elif skill_lvl < 0.3:
        variation = randint(-2, 0)

    mob_level = max(1, lvl + variation)

    classes = list(_ENEMY_WEIGHTS.keys())
    weights = list(_ENEMY_WEIGHTS.values())
    chosen_class = choices(classes, weights=weights)[0]

    return chosen_class(mob_level)