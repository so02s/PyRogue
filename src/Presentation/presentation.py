#Поле размером ~0x40 - 0x150 

import curses
from Domain.map import Level, Coridor, Room
from Domain import player, backpack
from Domain.stat_util import StatType
from Controller.menu import menu
from Datalayer.statistica import statistica
import time
import random
from .render_3d import Render3D
from .render_2d import Render2D
from .presentation_info import GraphMode

class Presentation():
    def __init__(self, stdscr: curses.window, level: Level) -> None:
        """
        stdscr - curses штука, класс window
        level - уровень игры
        """
        self.stdscr = stdscr
        self.map = level
        self.__init_color()
        self.renderer = Render2D(stdscr, level)
        
    def show_game(self):
        """
        Экран игры
        """
        self.renderer.render()
    
    def change_mode(self, mode: int):
        if mode == GraphMode.GRAPHIC_3D.value:
            self.renderer = Render3D(self.stdscr, self.map)
        else:
            self.renderer = Render2D(self.stdscr, self.map)
        

    def show_menu(self):
        """
        Экран основного меню
        """
        self.stdscr.erase()
        curses.curs_set(0)
        center_y, center_x = self.stdscr.getmaxyx()
        center_y //= 2
        center_x //= 2

        title = "ROGUE 1980 X9000"
        title2 = "by sorencoa & nilahugh"
        self.stdscr.addstr(center_y - 10, center_x - len(title)//2 + 2, title, curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(center_y - 9, center_x - len(title2)//2 + 2, title2, curses.color_pair(5) | curses.A_BOLD)
        for i, (item, _) in enumerate(menu.menu_items):
            y = center_y - 5 + i * 2
            x = center_x - len(item)//2
            if i == menu.selected_index:
                self.stdscr.addstr(y, x, f"> {item} <", curses.color_pair(6))
            else:
                self.stdscr.addstr(y, x, f"  {item}  ", curses.color_pair(5))
        
        instr = "Use '↑/↓' to change      'Enter' to select      'Q' to return"
        self.stdscr.addstr(center_y + 10, center_x - len(instr)//2 + 2, instr, curses.color_pair(5))
        self.stdscr.refresh()

    def show_settings_menu(self, current_mode: int):
        """
        Экран настроек: выбор режима графики (2D/3D).
        """
        self.stdscr.erase()
        curses.curs_set(0)
        max_y, max_x = self.stdscr.getmaxyx()
        center_y = max_y // 2
        center_x = max_x // 2

        title = "Settings"
        self.stdscr.addstr(center_y - 4, center_x - len(title)//2 + 2, title, curses.color_pair(5) | curses.A_BOLD)
        options = ["2D Graphics", "3D Graphics"]

        for i, opt in enumerate(options):
            y = center_y - 2 + i * 2
            x = center_x - len(opt)//2
            if i == current_mode:
                self.stdscr.addstr(y, x, f"> {opt} <", curses.color_pair(6))
            else:
                self.stdscr.addstr(y, x, f"  {opt}  ", curses.color_pair(5))

        instr = "Use '↑/↓' to change      'Enter' to select      'Q' to return"
        self.stdscr.addstr(center_y + 4, center_x - len(instr)//2 + 2, instr, curses.color_pair(5))
        self.stdscr.refresh()

    def show_inventory(self) -> None:
        """
        Экран инвентаря
        """
        self.stdscr.erase()
        self.renderer.draw_stats(0)

        max_y, max_x = self.stdscr.getmaxyx()
        mid_x = max_x // 2 + 2
        white_color = curses.color_pair(5)

        for y in range(3, max_y):
            self.stdscr.addch(y, mid_x - 2, '|', white_color)

        top_margin = 3
        box_width = (mid_x - 1) // 2
        box_height = (max_y - top_margin - 4) // 2

        positions = [
            (0, top_margin),
            (box_width, top_margin),
            (0, top_margin + box_height),
            (box_width, top_margin + box_height)
        ]

        all_items = backpack.get_all_items()
        
        for cat, (box_x, box_y) in zip(backpack.categories, positions):
            for i in range(box_height):
                for j in range(box_width):
                    ch = ' '
                    if i == 0 or i == box_height - 1:
                        if j == 0 or j == box_width - 1:
                            ch = '+'
                        else:
                            ch = '-'
                    elif j == 0 or j == box_width - 1:
                        ch = '|'
                    self.stdscr.addch(box_y + i, box_x + j, ch, white_color)

            title = f"{cat.capitalize()} {backpack.get_type_count(cat)}/9"
            self.stdscr.addstr(box_y + 1, box_x + 2, title, white_color)

            for idx, item in enumerate(backpack.get_type_list(cat)):
                global_idx = all_items.index(item)
                attr = curses.color_pair(6) if global_idx == backpack.index else white_color

                line = item.name
                if len(line) > box_width - 4:
                    line = line[:box_width - 7] + "..."
                self.stdscr.addstr(box_y + 3 + idx, box_x + 2, line, attr)

        self.stdscr.addstr(top_margin, mid_x, "Equipment and Effects", white_color)
        self.stdscr.addstr(top_margin + 2, mid_x, "Weapon: " + player.now_weapon(), white_color)
        self.stdscr.addstr(top_margin + 3, mid_x, "Press 'h' to unequip weapon", white_color)
        self.stdscr.addstr(top_margin + 5, mid_x, "Effects: ", white_color)
        if player._effects:
            line_y = top_margin + 5
            for e_type, (val, dur) in player._effects.items():
                if e_type == StatType.STRENGTH:
                    name = "Strench"
                elif e_type == StatType.DEXTERITY:
                    name = "Dexterity"
                elif e_type == StatType.HEALTH:
                    name = "Health"
                text = f"  {name} +{val} ({dur} movement)"
                self.stdscr.addstr(line_y, mid_x, text, white_color)
                line_y += 1
            gold_y = line_y + 1
        else:
            self.stdscr.addstr(top_margin + 5, mid_x, "  Nope", white_color)
            gold_y = top_margin + 7

        self.stdscr.addstr(gold_y, mid_x, f"Gold: {backpack.gold}", white_color)
        keys = backpack.get_type_list('key')
        if keys:
            self.stdscr.addstr(gold_y + 2, mid_x + 2, "Keys:", curses.color_pair(5))
            for i, key in enumerate(keys):
                self.stdscr.addstr(gold_y + 3 + i, mid_x + 2, f"  {key.name}", curses.color_pair(key.color))
        else:
            self.stdscr.addstr(gold_y + 2, mid_x + 2, "Keys: none", curses.color_pair(5))


        self.stdscr.refresh()

    def show_statistica(self):
        """
        Экран статистики
        """
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()

        headers = [
            "Treasures",
            "Lvl",
            "Enemies",
            "Food",
            "Potions",
            "Scrolls",
            "At.made",
            "At.hits",
            "Cells"
        ]
        weidth = (max_x // len(headers)) - 1
        header_line = " ".join(f"{h:>{weidth}}" for h in headers)
        center_x = (max_x - len(header_line)) // 2
        self.stdscr.addstr(0, center_x, header_line, curses.A_BOLD | curses.A_UNDERLINE)

        keys = [
            "amount_of_treasure", "lvl", "number_of_enemies",
            "amount_of_food", "number_of_elixirs", "number_of_scrolls",
            "number_of_attacks_made", "number_of_attacks_hits", "number_of_tiles"
        ]

        data_height = max_y - 5
        total = len(statistica.full_statistica)
        max_offset = max(0, total - data_height)
        offset = min(statistica.select_index, max_offset)

        for i in range(data_height):
            idx = offset + i
            if idx >= total:
                break
            entry = statistica.full_statistica[idx]
            row_parts = []
            for key in keys:
                val = str(entry.get(key, 0))
                row_parts.append(val.rjust(weidth))
            row_line = " ".join(row_parts)
            self.stdscr.addstr(1 + i, center_x, row_line)

        cansel_text = "To cancel press q"
        self.stdscr.addstr(max_y - 3, (max_x - len(cansel_text)) // 2, cansel_text)

        self.stdscr.refresh()

    def show_win(self):
        """
        Победный экран
        """
        self.stdscr.clear()
        s = "You win!"
        max_y, max_x = self.stdscr.getmaxyx()
        center_y = max_y // 2
        center_x = max_x // 2
        self.stdscr.addstr(1, center_x - len(s) // 2, s, curses.color_pair(8))
        self.draw_credits(s, "win")
    
    def draw_credits(self, s, status):
        max_y, max_x = self.stdscr.getmaxyx()
        center_y = max_y // 2
        center_x = max_x // 2
        self.stdscr.refresh()

        credits_lines = [
            "Над игрой работали:",
            "Эльф sorencoa",
            "и",
            "Сия nilahugh"
        ]
        y = max_y
        color = curses.color_pair(8)
        if status == "lose":
            color = curses.color_pair(9)
        while y > 2:
            self.stdscr.clear()
            if status == "win":
                self.draw_firework(5)
            else:
                self.draw_sad_face(5)
            self.stdscr.addstr(1, center_x - len(s) // 2, s, color)
            for i, line in enumerate(credits_lines):
                line_y = y + i
                if 0 <= line_y < max_y:
                    x = center_x - len(line) // 2
                    self.stdscr.addstr(line_y, x, line)
            self.stdscr.refresh()
            time.sleep(0.3)
            y -= 1

    def draw_firework(self, count):
        """Рисует хлопушки"""
        firework_pattern = [
            "  \\|/  ",
            "---•---",
            "  /|\\  "
        ]
        pattern_h = len(firework_pattern)
        pattern_w = max(len(line) for line in firework_pattern)
        max_y, max_x = self.stdscr.getmaxyx()
        if max_y <= pattern_h + 1 or max_x <= pattern_w + 1:
            return

        for _ in range(count):
            y = random.randint(0, max_y - pattern_h - 1)
            x = random.randint(0, max_x - pattern_w - 1)
            color = random.randint(1, 18)
            for i, line in enumerate(firework_pattern):
                try:
                    self.stdscr.addstr(y + i, x, line, curses.color_pair(color))
                except curses.error:
                    pass

    def draw_sad_face(self, count):
        """
        Рисует грустные мордочки в случайных местах экрана
        """
        face_pattern = [
        "     _____   ",
        "   (       ) ",
        "  (  o   o  )",
        "  (    ^  | )",
        " (        |  )",
        "  (       | )",
        "   (       ) ",
        "     _____   ",
        ]
        
        pattern_h = len(face_pattern)
        pattern_w = max(len(line) for line in face_pattern)
        max_y, max_x = self.stdscr.getmaxyx()

        if max_y <= pattern_h + 1 or max_x <= pattern_w + 1:
            return

        for _ in range(count):
            y = random.randint(0, max_y - pattern_h - 1)
            x = random.randint(0, max_x - pattern_w - 1)

            for i, line in enumerate(face_pattern):
                for j, ch in enumerate(line):
                    color_pair = 7 if ch == '|' else 17
                    try:
                        self.stdscr.addch(y + i, x + j, ch, curses.color_pair(color_pair))
                    except curses.error:
                        pass
                
    def show_no_data(self):
        """
        Отображение экрана, если нет сохраненных игр
        """
        self.stdscr.clear()
        s = "To unlock this start new game"
        s_press = "Press any button"
        center_y, center_x = self.stdscr.getmaxyx()
        center_y //= 2
        center_x //= 2
        self.stdscr.addstr(center_y, abs(center_x - len(s) // 2), s)
        self.stdscr.addstr(center_y + 1, abs(center_x - len(s_press) // 2), s_press, curses.color_pair(17))
        # self.stdscr.getch()
        
    @staticmethod
    def __init_color() -> None:
        """
        Инициалиация цвета
        """
        curses.curs_set(0)
        curses.start_color()
        
        curses.init_color(11, 0, 350, 0)     # Зелёный
        curses.init_color(14, 250, 50, 4)   # Красный
        curses.init_color(16, 400, 400, 400) # Серый

        curses.init_pair(1, 136, curses.COLOR_BLACK)  # Еда
        curses.init_pair(2, 160, curses.COLOR_BLACK)  # Зелья
        curses.init_pair(3, 229, curses.COLOR_BLACK)  # Свитки
        curses.init_pair(4, 129, curses.COLOR_BLACK)  # Оружие
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Инвентарь обычный; Призрак; Маг
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Инвентарь выделенный; Орк
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Игрок
        curses.init_pair(8, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Зомби
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)  # Вампир
        curses.init_pair(10, 197, curses.COLOR_BLACK)  # Цвет при атаке

        curses.init_pair(12, 11, curses.COLOR_BLACK) # Коридор 
        curses.init_pair(15, 14, curses.COLOR_BLACK) # Комнаты
        curses.init_pair(17, 16, curses.COLOR_BLACK) # Затемнение
    
        curses.init_pair(18, 221, curses.COLOR_BLACK)  #золото
    
    def msg(self, text: str) -> None:
        """
        Выводит сообщение в центре экрана в рамке и ждёт нажатия клавиши.
        """
        lines = text.split('\n')
        width = max(len(line) for line in lines) + 4
        height = len(lines) + 2
        start_y = self.map.max_y // 2 - height // 2
        start_x = self.map.max_x // 2 - width // 2

        for i in range(height):
            for j in range(width):
                if i == 0 or i == height - 1:
                    if j == 0 or j == width - 1:
                        ch = '+'
                    else:
                        ch = '-'
                else:
                    if j == 0 or j == width - 1:
                        ch = '|'
                    else:
                        ch = ' '
                self.stdscr.addch(start_y + i, start_x + j, ch)

        for i, line in enumerate(lines):
            self.stdscr.addstr(start_y + 1 + i, start_x + 2, line)

        self.stdscr.refresh()
        self.stdscr.getch()

    def draw_death_screen(self) -> None:
        """
        Экран смерти
        """
        self.stdscr.clear()
        self.draw_credits("GAMEOVER", "lose")