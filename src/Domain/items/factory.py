import random
from math import exp
from .food import Food
from .potion import Potion
from .scroll import Scroll
from .weapon import Weapon
from .treasure import Treasure
from .item import Item

_ITEM_TYPE_DATA = {
    Food: {
        'base_weight': 50,
        'alpha': 0,
    },
    Potion: {
        'base_weight': 15,
        'alpha': -0.05,
    },
    Scroll: {
        'base_weight': 10,
        'alpha': 0.05,
    },
    Weapon: {
        'base_weight': 25,
        'alpha': -0.055,
    },
    Treasure: {
        'base_weight': 0, 
        'alpha': 0,
    },
}

def create_rnd_item(lvl: int, skill_lvl: float = 0.5) -> Item:
    items = list(_ITEM_TYPE_DATA.keys())
    weights = {}
    target_base = 0.5
    target_adjustment = 1.0 + (skill_lvl - 0.5) * 0.4

    for cls in items:
        data = _ITEM_TYPE_DATA[cls]
        base = data['base_weight']
        alpha = data['alpha']
        target = target_base * target_adjustment
        exp_factor = exp(-alpha * (lvl - 1))
        weight = base * exp_factor + target * (1 - exp_factor)
        weights[cls] = max(weight, 0.01)

    chosen_class = random.choices(items, weights=list(weights.values()))[0]

    return chosen_class.random(lvl)