from Presentation import Presentation, GraphMode
from Domain import player, backpack, Coordinate, Level
from Domain.items import Item
from curses import window
import Controller.layout as layout
from Controller.sound_controller import sounds
from .states import GameStates
from .menu import menu
from Datalayer.datalayer import datalayer
from .utils import GAMEOVER
from Datalayer.statistica import statistica

class Controller():
    def __init__(self, stdscr: window) -> None:
        self.stdscr = stdscr
        self.current_layout = 'wasd'
        self.key_map = layout.LAYOUTS[self.current_layout]
        self.map = Level(self.stdscr)
        # self.map.test_spawn_items_in_start_room(10)
        self.state = GameStates.MENU
        self.graph_settings_check = GraphMode.GRAPHIC_2D.value
        self.graph_settings = GraphMode.GRAPHIC_2D.value
        self.view = Presentation(self.stdscr, self.map)

        self.data = datalayer(self.map)

    def start(self) -> None:
        """
        Запуск игры
        """
        sounds.intro.play()
        self.FMS()
    
    def FMS(self) -> None:
        """
        Finite Machine State - конечный автомат для этой игры
        """
        while(True):
            if self.state == GameStates.MENU:
                self.view.show_menu()
            elif self.state == GameStates.GAME:
                sounds.intro.stop()
                self.data.delete_progress()
                self.view.show_game()
                self.data.add_information() # сохраняет каждый шаг
            elif self.state == GameStates.BACKPACK:
                self.view.show_inventory()
            elif self.state == GameStates.SETTINGS:
                self.view.show_settings_menu(self.graph_settings_check)
            elif self.state == GameStates.STATISTICA:
                self._load_statistica(key)
            elif self.state == GameStates.LOAD_GAME:
                self._load_data()
                self.state = GameStates.GAME
            elif self.state == GameStates.WIN:
                self._handle_win()
                self.state = GameStates.STATISTICA
            elif self.state == GameStates.DEATH:
                self._handle_death()
                self.state = GameStates.STATISTICA
            elif self.state == GameStates.EXIT:
                break

            key = self.stdscr.getch()

            if self.state == GameStates.MENU:
                self._handle_menu_input(key)
            elif self.state == GameStates.GAME:
                if self._handle_game_input(key):
                    self._game_step()
            elif self.state == GameStates.BACKPACK:
                self._handle_inventory_input(key)
            elif self.state == GameStates.STATISTICA:
                self._handle_only_quit(key)
                sounds.gameover.stop()
            elif self.state == GameStates.SETTINGS:
                self._handle_settings_input(key)
            
            if self.state == GameStates.NEW_GAME:
                menu.set_active_game()
                self.map.restart()
                self.state = GameStates.GAME

    def _load_statistica(self, key):
        """
        ???
        """
        if key in layout.KEY_DOWN:
            statistica.next()
        elif key in layout.KEY_UP:
            statistica.prev()
        statistica.statistica_sort()
        # data = {}
        if len(statistica.full_statistica) != 0:
            self.view.show_statistica()
        else:
            self.view.show_no_data()
            self.state = GameStates.MENU


    def _load_data(self):
        """
        Загружает данные
        """
        self.map._clear_level()
        data = self.data.load_last_game()
        if len(data) != 0:
            self.map.load_level(data)
            self.view.show_game()
        else:
            self.view.show_no_data()
            self.state = GameStates.MENU

    def _game_step(self) -> None:
        """
        Логика одного шага в игре
        """

        statistica.number_of_tiles += 1
        
        if player.crd == self.map.exit:
            if self.map.lvl == GAMEOVER:
                self.state = GameStates.WIN
            else:
                sounds.next_level.play()
                self.map.next_level()
            return
        
        obj = self.map.get_obj(player.crd)
        if obj:
            self._pick_up_item(obj)
        
        self.map.move_mobs()

        player.tick_effects()
        
        harm = self.map.check_player_harm()
        player.hurt(harm)

        if player.is_dead():
            self.state = GameStates.DEATH

    def _handle_settings_input(self, key: int) -> None:
        """
        Обработка клавиш, экран настроек
        """
        if key in layout.KEY_DOWN:
            if self.graph_settings_check < 1:
                self.graph_settings_check += 1
        elif key in layout.KEY_UP:
            if self.graph_settings_check > 0:
                self.graph_settings_check -= 1
        elif key in layout.KEY_ENTER:
            self.graph_settings = self.graph_settings_check
        elif key in layout.QUIT_TO_MENU:
            self.graph_settings_check = self.graph_settings
            self.view.change_mode(self.graph_settings)
            self.state = GameStates.MENU
        
    def _handle_game_input(self, key: int) -> bool:
        """
        Обработка клавиш, экран игры
        """
        if player.is_sleep:
            player.is_sleep = False
            return True

        if key in layout.BACKPACK_OPEN_CLOSE:
            backpack.set_index_to_start()
            self.state = GameStates.BACKPACK
            return True
        elif key in layout.QUIT_TO_MENU:
            self.state = GameStates.MENU
            return True

        if self.graph_settings == GraphMode.GRAPHIC_2D.value:
            d_y, d_x = self._handle_input_2d(key)
        else:
            d_y, d_x = self._handle_input_3d(key)
        
        if d_y == 0 and d_x == 0:
            return False

        n_y, n_x = d_y + player.y, d_x + player.x
        if self.map.is_door(n_y, n_x):
            door_color = self.map.get_door_color(n_y, n_x)
            if backpack.has_key(door_color):
                sounds.door_open.play()
                backpack.del_key(door_color)
                self.map.delete_door(n_y, n_x)
            else:
                return False
            
        if not self.map.is_walkable(n_y, n_x):
            return False
        
        if self.map.is_mob(n_y, n_x):
            self._attack_mob((n_y, n_x))
        else:
            player.move((d_y, d_x))
        return True

    def _handle_input_2d(self, key: int) -> tuple:
        """
        Обработка 2d клавиш в игре
        """
        if key in self.key_map:
            return self.key_map[key]
        return (0, 0)
    
    def _handle_input_3d(self, key: int) -> tuple:
        """
        Обработка 3d клавиш в игре
        """
        if key in layout.KEY_LEFT:
            player.direction_left()
            return (0, 0)
        elif key in layout.KEY_RIGHT:
            player.direction_right()
            return (0, 0)
        elif key in layout.KEY_UP:
            return layout.DIRECTION_OFFSETS[player.direction.value]
        elif key in layout.KEY_DOWN:
            backward_dir = (player.direction.value + 2) % 4
            return layout.DIRECTION_OFFSETS[backward_dir]
        return (0, 0)

    def _handle_only_quit(self, key: int) -> None:
        """
        Обработка клавиш, толькод для выхода либо продолжения
        """
        if key in layout.QUIT_TO_MENU:
            self.state = GameStates.MENU
        else:
            self.state = GameStates.GAME
        

    def _handle_inventory_input(self, key: int) -> None:
        """
        Обработка клавиш, экран инвентаря
        """
        if key in layout.KEY_DOWN:
            backpack.move_down()
        elif key in layout.KEY_UP:
            backpack.move_up()
        elif key in layout.KEY_ENTER:
            backpack.use_item(self.map)
        elif key in layout.UNEQUIP_WEAPON:
            backpack.unequip_weapon(self.map)
        elif key in layout.BACKPACK_OPEN_CLOSE or key in layout.QUIT_TO_MENU:
            self.state = GameStates.GAME
    
    def _handle_menu_input(self, key: int) -> None:
        """
        Обработка клавиш, экран меню
        """
        if key in layout.KEY_DOWN:
            menu.next()
        elif key in layout.KEY_UP:
            menu.prev()
        elif key in layout.KEY_ENTER:
            menu.use_command(self)
        elif key in layout.QUIT_TO_MENU:
            self.state = GameStates.EXIT
    
    def _pick_up_item(self, event: Item) -> None:
        """
        Поднятие предмета с карты. Вызывает соо, если рюкзак заполнен
        """
        if(backpack.add_item(event)):
            self.map.del_obj(player.crd)
        else:
            self.view.msg("Backpack is full!")

    def _handle_death(self) -> None:
        """
        Отрисовка экрана смерти + перегенерация уровня
        """
        player.skill_lvl = max(0.1, player.skill_lvl - 0.1)
        statistica.update_statistica()
        sounds.gameover.play()
        self.view.draw_death_screen()
        self.map.restart()
        player.restart()
        backpack.clear()

    def _handle_win(self):
        """
        Отрисовка экрана победы + перегенерация уровня
        """
        player.skill_lvl = min(1, player.skill_lvl + 0.1)
        statistica.update_statistica()
        sounds.win.play()
        self.view.show_win()
        self.map.restart()
        player.restart()
        backpack.clear()

    def _attack_mob(self, crd: Coordinate) -> None:
        """
        Нанести монстру (расположенному на crd) урон
        """
        mob = self.map.get_mob(crd)
        if mob is None:
            return

        if mob.hit(player.dexterity):
            mob.hurt(player.attack())
            statistica.number_of_attacks_made += 1
        else:
            sounds.miss_sound.play()
            statistica.number_of_attacks_hits += 1
        
        if not mob.is_alive():
            percentage = (player.current_health / player.maximum_health) * 100
            if percentage < 30:
                player.skill_lvl = max(0.1, player.skill_lvl - 0.05)
            elif percentage > 70:
                player.skill_lvl = min(1, player.skill_lvl + 0.05)
            self.map.kill_mob(crd)
            statistica.number_of_enemies += 1