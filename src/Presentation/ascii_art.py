from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Sprite:
    lines: List[str]
    physical_height: Optional[float] = None
    physical_width: Optional[float] = None

def normalize_sprite(sprite_lines):
    max_len = max(len(line) for line in sprite_lines)
    return [line.ljust(max_len) for line in sprite_lines]

SPRITES = {
    'key': Sprite(
        lines=[
            " ██ ",
            " █  ",
            " ██ ",
            " █  ",
            "█ █ ",
            " █  "
        ],
        physical_height=0.1,
        physical_width=0.1
    ),
    'сокровище': Sprite(
        lines=[
            " ███ ",
            "█   █",
            "█ █ █",
            "█   █",
            " ███ "
        ],
        physical_height=0.1,
        physical_width=0.1
    ),
    's': Sprite(
        lines=[
            "  ██        ",
            " ████████   ",
            "█        █  ",
            "         █  ",
            " ████████   ",
            "█          █",
            " ██████████ ",
        ],
        physical_height=0.1,
        physical_width=0.6
    ),
    'z': Sprite(
        lines=[
            "█████",
            "    █",
            "  ██ ",
            " █   ",
            "█████"
        ],
        physical_height=0.1,
        physical_width=0.5
    ),
    'v': Sprite(
        lines=[
            "█   █",
            "█   █",
            "█   █",
            " █ █ ",
            "  █  "
        ],
        physical_height=0.1,
        physical_width=0.1
    ),
    'm': Sprite(
        lines=[
            "█    ",
            "█████",
            "█ █ █",
            "█ █ █",
            "█ █ █"
        ],
        physical_height=0.1,
        physical_width=0.1
    ),
    'O': Sprite(
        lines=[
            " ███ ",
            "█   █",
            "█   █",
            "█   █",
            " ███ "
        ],
        physical_height=0.1,
        physical_width=0.1
    ),
    'g': Sprite(
        lines=[
        "     _____   ",
        "   (       ) ",
        "  (  o   o  )",
        "  (    ^  | )",
        " (        |  )",
        "  (       | )",
        "   (       ) ",
        "     _____   ",
        ],
        physical_height=0.1,
        physical_width=0.1
    ),
    'food': Sprite(
        lines=[
            "    █  ",
            "  █    ",
            "███████",
            "█     █",
            " █████ "
        ],
        physical_height=.01,
        physical_width=0.01
    ),
    'potion': Sprite(
        lines=[
            " ███ ",
            " █ █ ",
            "█ █ █",
            "█   █",
            " ███ "
        ],
        physical_height=0.1,
        physical_width=0.5
    ),
    'scroll': Sprite(
        lines=[
            "   ██",
            "  █ █",
            "  █  ",
            "█ █  ",
            "██   "
        ],
        physical_height=0.1,
        physical_width=0.5
    ),
    'weapon': Sprite(
        lines=[
            "  █  ",
            " █ █ ",
            " █ █ ",
            "█████",
            "  █  "
        ],
        physical_height=0.1,
        physical_width=0.5
    ),
    'exit': Sprite(lines=[
            "█████",
            "█████",
            "█████",
            "█████",
            "█████"
        ], physical_height=0.15, physical_width=1)
}
