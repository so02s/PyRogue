import curses

LAYOUTS = {
    'wasd': {
        ord('w'): [-1, 0],
        ord('a'): [0, -1],
        ord('s'): [1, 0],
        ord('d'): [0, 1],
        ord('ц'): [-1, 0],
        ord('ф'): [0, -1],
        ord('ы'): [1, 0],
        ord('в'): [0, 1],
        curses.KEY_UP:    [-1, 0],
        curses.KEY_DOWN:  [1, 0],
        curses.KEY_LEFT:  [0, -1],
        curses.KEY_RIGHT: [0, 1],
    }
}

DIRECTION_OFFSETS = {
    0: (-1, 0),
    1: (0, 1),
    2: (1, 0),
    3: (0, -1),
}

BACKPACK_OPEN_CLOSE = [ord('e'), ord('у')]
QUIT_TO_MENU = [ord('q'), ord('й'), 27]

KEY_UP = [curses.KEY_UP, ord('w'), ord('ц')]
KEY_DOWN  = [curses.KEY_DOWN, ord('s'), ord('ы')]
KEY_LEFT = [curses.KEY_LEFT, ord('a'), ord('ф')]
KEY_RIGHT = [curses.KEY_RIGHT, ord('d'), ord('в')]

KEY_ENTER = [curses.KEY_ENTER, ord('\n')]

UNEQUIP_WEAPON = [ord('h'), ord('р')]