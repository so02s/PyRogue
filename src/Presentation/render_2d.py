import curses
from Domain import Level, player, backpack
from Domain.map import Room, Coridor
from .render import Renderer

class Render2D(Renderer):
    def __init__(self, stdscr: curses.window, level: Level):
        """
        stdscr - curses штука, класс window
        level - уровень игры
        """
        self.stdscr = stdscr
        self.map = level
        self.radius_view = 3 # дальность обзора при частичной отрисовке
    
    def render(self):
        """
        Отрисовка
        """
        self.stdscr.erase()
        for r in self.map.rooms:
            self.draw_room(r)
        for c in self.map.corridors:
            self.draw_coridor(c)
        
        self.draw_exit()
        self.draw_events()
        self.draw_character()
        self.draw_stats(self.map.max_y - 2)

    def draw_stats(self, y: int = 0) -> None:
        """
        Статистика для экрана игры
        """
        self.stdscr.addstr(y, 0, \
            f"LVL: {self.map.lvl}\t\t"
            f"HP: {player.current_health}({player.maximum_health})\t\t"
            f"ATTACK: {player.attack()}\t\t"
            f"GOLD: {backpack.gold}\t\t"
            )
    
    def draw_room(self, room: Room) -> None:
        """
        Отображение комнат
        """
        current_id = self.map.get_room_id_by_crd([player.y, player.x])
        player_on_wall = False
        if room.id == current_id:
            if (player.y == room.y or player.y == room.y + room.height - 1 or
                player.x == room.x or player.x == room.x + room.width - 1):
                player_on_wall = True

        for i in range(room.height):
            for j in range(room.width):
                if room.id == current_id:
                    room.visited = True
                    y = room.y + i
                    x = room.x + j
                    is_wall = (i == 0 or i == room.height - 1 or j == 0 or j == room.width - 1)

                    if not player_on_wall:
                        if is_wall:
                            self.stdscr.addch(y, x, ord('#'), curses.color_pair(15))
                        else:
                            self.stdscr.addch(y, x, ord('.'), curses.color_pair(12))

                    elif player_on_wall:
                        if abs(y - player.y) < self.radius_view and abs(x - player.x) < self.radius_view:
                            if is_wall:
                                self.stdscr.addch(y, x, ord('#'), curses.color_pair(15))
                            else:
                                self.stdscr.addch(y, x, ord('.'), curses.color_pair(12))
                                
                elif room.visited:
                        color = curses.color_pair(17)
                        if i == 0 or i == room.height - 1 or j == 0 or j == room.width - 1:
                            self.stdscr.addch(room.y + i, room.x + j, ord("#"), color)

    def draw_coridor(self, one_corridor: Coridor) -> None:
        """
        Отображение коридоров
        """
        color = curses.color_pair(12)
        id = self.map.get_room_id_by_crd([player.y, player.x])
        y, x = one_corridor.points[0][0], one_corridor.points[0][1]

        if one_corridor.room2_id == id:
            points_len = len(one_corridor.points)
            y, x = one_corridor.points[points_len - 1][0], one_corridor.points[points_len - 1][1]
            one_corridor.enter = one_corridor.room2_id
        if one_corridor.room1_id == id:
            one_corridor.enter = one_corridor.room1_id

        ch = self.stdscr.inch(y, x)
        char = chr(ch & 0xFF)
        if char == '#':
            self.stdscr.addch(y, x, ord("."), color)
        if (player.y, player.x) in one_corridor.points:
            for py, px in one_corridor.points:
                if abs(py - player.y) + abs(px - player.x) <= self.radius_view:
                    self.stdscr.addch(py, px, ord('.'), color)
            if one_corridor.enter == one_corridor.room1_id:
                opposite_door = one_corridor.points[-1]
            elif one_corridor.enter == one_corridor.room2_id:
                opposite_door = one_corridor.points[0]
            if (abs(player.y - opposite_door[0]) + abs(player.x - opposite_door[1]) == 1 and
                    (player.y, player.x) != opposite_door):
                one_corridor.visitable = True

        elif one_corridor.visitable:
            color = curses.color_pair(17)
            for y, x in one_corridor.points:
                self.stdscr.addch(y, x, ord("."), color) 

    def draw_exit(self) -> None:
        """
        Отображение выхода на карте
        """
        y, x = self.map.exit
        if self.in_radius(y, x):
            self.stdscr.addch(y, x, "█")

    def draw_events(self) -> None:
        """
        Отображение ивентов на карте
        """
        for (y, x), door in self.map.doors.items():
            if self.in_radius(y, x):
                self.stdscr.addch(y, x, door.symbol, curses.color_pair(door.color))

        for (y, x), mob in self.map.mobs.items():
            if self.in_radius(y, x):
                if hasattr(mob, 'invisible') and mob.invisible:
                    continue
                self.stdscr.addch(y, x, mob.symbol, curses.color_pair(mob.color))

        for (y, x), obj in self.map.objects.items():
            if self.in_radius(y, x):
                self.stdscr.addch(y, x, obj.symbol, curses.color_pair(obj.color))

    def draw_character(self) -> None:
        """
        Отображение игрока
        """
        self.stdscr.addch(player.y, player.x, player.symbol, curses.color_pair(player.color))

    def in_radius(self, y, x) -> bool:
        """
        ???
        """
        res = False
        ch = self.stdscr.inch(y, x)
        char = chr(ch & 0xFF)
        if char == '.' and (ch & curses.color_pair(12)) == curses.color_pair(12):
            res = True
        return res
