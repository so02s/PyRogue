import curses, math
from Domain import Level, player, backpack
from .render import Renderer
from Domain.stat_util import Direction
from .ascii_art import SPRITES, Sprite
from dataclasses import dataclass
from typing import List

@dataclass
class SpriteInstance:
    y: float
    x: float
    sprite: any
    color: int
    height: int
    width: int
    dist: float = 0
    angle: float = 0

    def __post_init__(self):
        self.height = len(self.sprite)
        self.width = len(self.sprite[0])


class Render3D(Renderer):
    SHADES = [' ', '░', '▒', '▓', '█']
    dir_angles = {
        0: -math.pi/2,
        1: 0,
        2: math.pi/2,
        3: math.pi
    }

    def __init__(self, stdscr: curses.window, level: Level) -> None:
        """
        stdscr - curses штука, класс window
        level - уровень игры
        """
        self.stdscr = stdscr
        self.map = level
        self.fov = math.pi / 3
        self.half_fov = self.fov / 2

    def render(self):
        self.stdscr.erase()
        self.ray_casting()
        self.draw_minimap()
        self.draw_stats(self.map.max_y - 2)

    def draw_minimap(self):
        """
        Отрисовывает мини-карту в правом верхнем углу
        """
        max_y, max_x = self.stdscr.getmaxyx()
        map_size = 5
        offset = map_size // 2
        start_y = 0
        start_x = max_x - map_size - 2

        py, px = player.y, player.x

        for dy in range(-offset, offset + 1):
            for dx in range(-offset, offset + 1):
                ny = py + dy
                nx = px + dx
                screen_y = start_y + dy + offset
                screen_x = start_x + dx + offset
                if not (0 <= screen_y < max_y and 0 <= screen_x < max_x):
                    continue

                if ny < 0 or ny > self.map.max_y or \
                    nx < 0 or ny > self.map.max_x:
                    ch = ' '
                    color = 0

                if (ny, nx) == (py, px):
                    if player.direction == Direction.UP:
                        ch = '▶'
                    elif player.direction == Direction.RIGHT:
                        ch = '▲'
                    elif player.direction == Direction.DOWN:
                        ch = '◀'
                    elif player.direction == Direction.LEFT:
                        ch = '▼'
                    else:
                        ch = player.symbol
                    color = curses.color_pair(player.color)
                elif self.map.exit == (ny, nx):
                    ch = '█'
                    color = curses.color_pair(5)
                elif self.map.is_door(ny, nx):
                    door = self.map.doors[(ny, nx)]
                    ch = door.symbol
                    color = curses.color_pair(door.color)
                elif self.map.is_mob(ny, nx):
                    mob = self.map.get_mob((ny, nx))
                    ch = mob.symbol
                    color = curses.color_pair(mob.color)
                elif (ny, nx) in self.map.objects:
                    obj = self.map.objects[(ny, nx)]
                    ch = obj.symbol
                    color = curses.color_pair(obj.color)
                elif self.map.is_walkable(ny, nx):
                    ch = '.'
                    color = curses.color_pair(12)
                else:
                    ch = '#'
                    color = curses.color_pair(15)
                self.stdscr.addch(screen_y, screen_x, ch, color)
    
    def ray_casting(self):
        """
        Чертов алгоритм RAY CASTINGAAAA
        """
        max_rows, max_cols = self.map.max_y, self.map.max_x
        player_angle = self.dir_angles[player.direction.value]

        cam_x = player.x + 0.5
        cam_y = player.y + 0.5

        z_buffer = [float('inf')] * max_cols

        for col in range(max_cols):

            rel_angle = (col - max_cols / 2) / (max_cols / 2) * self.half_fov
            angle = player_angle + rel_angle
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            map_x = int(cam_x)
            map_y = int(cam_y)
                                                                                                                                 
            if cos_a > 0:
                step_x = 1
                side_dist_x = (map_x + 1 - cam_x) / cos_a
            elif cos_a < 0:
                step_x = -1
                side_dist_x = (cam_x - map_x) / -cos_a
            else:
                step_x = 0
                side_dist_x = float('inf')

            if sin_a > 0:
                step_y = 1
                side_dist_y = (map_y + 1 - cam_y) / sin_a
            elif sin_a < 0:
                step_y = -1
                side_dist_y = (cam_y - map_y) / -sin_a
            else:
                step_y = 0
                side_dist_y = float('inf')

            hit = False
            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += 1 / abs(cos_a) if cos_a != 0 else float('inf')
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += 1 / abs(sin_a) if sin_a != 0 else float('inf')
                    map_y += step_y
                    side = 1

                if not (0 <= map_y < self.map.max_y and 0 <= map_x < self.map.max_x):
                    break

                if not self.map.is_walkable(map_y, map_x) or self.map.is_door(map_y, map_x):
                    hit = True
                    if side == 0:
                        dist = (map_x - cam_x + (1 - step_x)/2) / cos_a
                    else:
                        dist = (map_y - cam_y + (1 - step_y)/2) / sin_a
                    dist *= math.cos(angle - player_angle)

            if hit:
                wall_color_pair = curses.color_pair(15)
                if self.map.is_door(map_y, map_x):
                    color = self.map.get_door_color(map_y, map_x)
                    wall_color_pair = curses.color_pair(color)

                if dist <= 0 or math.isinf(dist):
                    wall_height = max_rows
                else:
                    wall_height = int(max_rows / dist)
                wall_height = min(wall_height, max_rows)

                top = (max_rows - wall_height) // 2
                bottom = top + wall_height

                z_buffer[col] = dist
                
                wall_char = self.get_wall_char(dist, side)

                for row in range(top, bottom - 1):
                    if 0 <= row < max_rows:
                        self.stdscr.addch(row, col, wall_char, wall_color_pair)

                for row in range(bottom, max_rows - 1):
                    if 0 <= row < max_rows:
                        self.stdscr.addch(row, col, '.')

                for row in range(0, top - 1):
                    if 0 <= row < max_rows:
                        self.stdscr.addch(row, col, ' ')

            else:
                for row in range(max_rows - 1):
                    if 0 <= row < max_rows:
                        self.stdscr.addch(row, col, '.')

        self.draw_sprites(z_buffer, cam_x, cam_y)

    def draw_sprites(self, z_buffer, cam_x, cam_y):
        max_cols = self.map.max_x
        player_angle = self.dir_angles[player.direction.value]
        sprites: List[SpriteInstance] = []

        for (y, x), mob in self.map.mobs.items():
            sprite: Sprite = SPRITES.get(mob.type)
            sprites.append(SpriteInstance(y + 0.5, x + 0.5, sprite.lines, curses.color_pair(mob.color), sprite.physical_height, sprite.physical_width))

        for (y, x), obj in self.map.objects.items():
            sprite: Sprite = SPRITES.get(obj.type)
            sprites.append(SpriteInstance(y + 0.5, x + 0.5, sprite.lines, curses.color_pair(obj.color), sprite.physical_height, sprite.physical_width))

        sprite: Sprite = SPRITES.get('exit')
        y, x = self.map.exit
        sprites.append(SpriteInstance(y + 0.5, x + 0.5, sprite.lines, curses.color_pair(5), sprite.physical_height, sprite.physical_width))

        for s in sprites:
            dx = s.x - cam_x
            dy = s.y - cam_y
            s.dist = math.hypot(dx, dy)
            s.angle = math.atan2(dy, dx)

        sprites.sort(key=lambda s: s.dist, reverse=True)

        for s in sprites:
            diff = s.angle - player_angle
            while diff > math.pi:
                diff -= 2 * math.pi
            while diff < -math.pi:
                diff += 2 * math.pi

            if abs(diff) > self.half_fov:
                continue

            screen_x = int((diff / self.half_fov) * (max_cols / 2) + max_cols / 2)
            if screen_x < 0 or screen_x >= max_cols:
                continue

            if s.dist >= z_buffer[screen_x]:
                continue

            self.draw_sprite(s, screen_x, z_buffer)

    def draw_sprite(self, sprite: SpriteInstance, screen_x, z_buffer, height: float = 1, width: float = 1):
        """
        Рисует многострочный спрайт в заданной позиции
        """
        max_rows, max_cols = self.map.max_y, self.map.max_x

        s_screen_h = int(max_rows * height / sprite.dist) if sprite.dist > 0 else max_rows
        s_screen_h = min(max(1, s_screen_h), max_rows)
        
        s_screen_w = int(sprite.width * s_screen_h / sprite.height * width)

        top = (max_rows - s_screen_h) // 2
        bottom = top + s_screen_h
        left = screen_x - s_screen_w // 2
        right = left + s_screen_w

        for col in range(left, right):
            if col < 0 or col >= max_cols:
                continue
            if sprite.dist >= z_buffer[col]:
                continue
            src_col = (col - left) * sprite.width // s_screen_w
            src_col = max(0, min(src_col, sprite.width - 1))
            for row in range(top, bottom):
                if row < 0 or row >= max_rows:
                    continue
                src_row = (row - top) * sprite.height // s_screen_h
                src_row = max(0, min(src_row, sprite.height - 1))
                ch = sprite.sprite[src_row][src_col]
                if ch != ' ':
                    self.stdscr.addch(row, col, ch, sprite.color)

    def get_wall_char(self, dist, side):
        attenuation = 0.2
        brightness = 1 / (1 + dist * attenuation)

        if side == 1:
            brightness *= 0.8

        brightness = max(0, min(1, brightness))

        idx = int(brightness * (len(self.SHADES) - 1))
        return self.SHADES[idx]

    def draw_room(self, room):
        pass
    
    def draw_coridor(self, corridor):
        pass

    
    def draw_exit(self):
        pass

    
    def draw_events(self):
        pass

    
    def draw_character(self):
        pass

    
    def draw_stats(self, y):
        """
        Отображение статистики
        """
        self.stdscr.addstr(y, 0,
            f"LVL: {self.map.lvl}\t"
            f"HP: {player.current_health}({player.maximum_health})\t"
            f"ATTACK: {player.attack()}\t"
            f"GOLD: {backpack.gold}\t")