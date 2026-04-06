from random import randint, choice
from collections import deque
from curses import window
from typing import List, Dict, Optional, Union
from .room import Room
from .coridor import Coridor
from Domain import Coordinate, player, backpack
from Domain.enemies import create_rnd_enemy, Enemy
from Domain.items import create_rnd_item, Item, Treasure
from .door import DoorColor, Door
from .key import Key
from Datalayer.statistica import statistica
from .door import DoorColor, Door
from .key import Key

class Level:
    def __init__(self, stdscr: window) -> None:
        """
        stdscr - прикол из cursor (это window класс)
        max_x, max_y - края окна
        lvl - уровень подземелья
        """
        self.stdscr = stdscr
        self.max_y, self.max_x = stdscr.getmaxyx()
        self.lvl = 1

        self.rooms: List[Room] = [] 
        self.corridors: List[Coridor] = []
        self.doors: Dict[Coordinate, Door] = {}
        self.walkable: set[Coordinate] = set()
        self.objects: Dict[Coordinate, Item] = {}
        self.mobs: Dict[Coordinate, Enemy] = {}
        self.start_room_id: Optional[int] = None

        self._generate_level()

    def restart(self) -> None:
        """
        Перегенерация карты, стартуем с 1-го уровня
        """
        self.lvl = 1
        self._clear_level()
        self._generate_level()
        player.restart()
        backpack.clear()

    def _generate_level(self) -> None:
        """
        Генерация уровня
        """
        self.rooms = self._generate_rooms()
        self.corridors = self._generate_corridor()
        self.build_walkable()
        player.set_crd(self._get_rnd_crd())
        self.start_room_id = self.get_room_id_by_crd(player.crd)
        self._generate_objects()
        self._generate_mobs()
        self._place_exit_farthest_room(self.start_room_id)
        self._generate_doors()
        self._generate_keys()
        # self._place_exit_with_player(self.start_room_id)
    
    def _clear_level(self) -> None:
        """
        Очистка уровня
        """
        self.objects.clear()
        self.mobs.clear()
        self.rooms.clear()
        self.doors.clear()
        self.corridors.clear()
        self.walkable.clear()

    def _generate_entities(self, base_num: int, modifier: int, create_func, add_func, **kwargs) -> None:
        """
        Генерирует указанное количество сущностей и размещает их в случайных комнатах, исключая стартовую.
        """
        num = max(1, base_num + modifier)

        room_ids = [i for i in range(self.rooms_amount()) if i != self.start_room_id]
        if not room_ids:
            room_ids = list(range(self.rooms_amount()))

        for _ in range(num):
            room_id = choice(room_ids)
            cell = self._get_rnd_free_crd(room_id)
            if cell is None:
                continue
            entity = create_func(**kwargs)
            add_func(entity, cell)

    def _generate_mobs(self):
        """
        Генерирует врагов на уровне. Количество врагов определяется уровнем подземелья
        и навыком игрока: чем выше навык, тем больше врагов.
        """
        base_num = 6 + self.lvl
        if player.skill_lvl > 0.7:
            modifier = randint(2, 4)
        elif player.skill_lvl < 0.3:
            modifier = randint(-2, 0)
        else:
            modifier = randint(-1, 1)
        self._generate_entities(base_num, modifier, create_rnd_enemy, self.add_mob, lvl=self.lvl, skill_lvl=player.skill_lvl)
    
    def _generate_objects(self) -> None:
        """
        Генерирует предметы на уровне. Количество предметов убывает с глубиной подземелья.
        Навык игрока влияет на количество: слабый игрок получает больше предметов, сильный — меньше.
        """
        base_num = max(3, 8 - (self.lvl - 1) * 5 // 20)
        if player.skill_lvl > 0.7:
            modifier = randint(-2, 1)
        elif player.skill_lvl < 0.3:
            modifier = randint(1, 3)
        else:
            modifier = randint(-1, 1)
        self._generate_entities(base_num, modifier, create_rnd_item, self.add_obj, lvl=self.lvl, skill_lvl=player.skill_lvl)

    def _generate_rooms(self) -> List[Room]:
        """
        Генерация 9-ти комнат
        """
        max_y, max_x = self.stdscr.getmaxyx()
        cell_height = max_y // 3  
        cell_width = max_x // 3
    
        rooms = []

        MIN_HEIGHT = 5
        MIN_WIDTH = 7

        id = 0
        for row in range(3):
            for col in range(3):
                center_y = (row * cell_height) + (cell_height // 2)
                center_x = (col * cell_width) + (cell_width // 2)
                jitter_y = randint(-cell_height//9, cell_height//9)
                jitter_x = randint(-cell_width//9, cell_width//9)
            
                max_h = min(10, cell_height - 4)
                max_w = min(18, cell_width - 4)
                low_h = min(MIN_HEIGHT, max_h)
                low_w = min(MIN_WIDTH, max_w)
                
                height = randint(low_h, max_h)
                width  = randint(low_w, max_w)

                new_y = max(1, min(center_y + jitter_y - height//2, max_y - height - 2))
                new_x = max(1, min(center_x + jitter_x - width//2, max_x - width - 1))
            
                new_room = Room(new_x, new_y, height, width, id)
                id += 1
                rooms.append(new_room)
    
        return rooms

    def rooms_amount(self) -> int:
        """
        Количество комнат
        """
        return len(self.rooms)
    
    def _generate_corridor(self) -> List:
        """
        Генерация коридоров
        """
        corridors = []
        candidate_rooms = set(range(self.rooms_amount())) 
 
        grid_neighbors = {
            0: [1, 3],      # 0: право, низ
            1: [0, 2, 4],   # 1: лево, право, низ  
            2: [1, 5],      # 2: лево, низ
            
            3: [0, 4, 6],   # 3: верх, право, низ
            4: [1, 3, 5, 7],# 4: верх, лево, право, низ
            5: [2, 4, 8],   # 5: верх, лево, низ
            
            6: [3, 7],      # 6: верх, право
            7: [4, 6, 8],   # 7: верх, лево, право
            8: [5, 7]       # 8: верх, лево
        }
        
        while candidate_rooms:
            room1_id = candidate_rooms.pop()
            room1 = self.rooms[room1_id]
            available_neighbors = [nid for nid in grid_neighbors.get(room1_id, []) 
                                if nid in candidate_rooms]
            
            if available_neighbors:
                room2_id = choice(available_neighbors)
                room2 = self.rooms[room2_id]
                x1, y1, x2, y2 = self._get_wall_point(room1, room2, room1_id, room2_id)

                corridor = Coridor(x1, y1, x2, y2, room1_id, room2_id)
                corridor.generate_points()
                corridors.append(corridor)
        
        return corridors
    
    def _get_rnd_crd(self, room_id: int = None) -> Coordinate:
        """
        Вернут рандомные координаты внутри комнаты. Может быть вызвана с id.
        """
        if room_id == None:
            room = choice(self.rooms)
        else:
            room = self.rooms[room_id]
        y = randint(room.y + 1, room.y_end - 1)
        x = randint(room.x + 1, room.x_end - 1)
        return (y, x)
    
    def _get_rnd_free_crd(self, room_id: int, max_attempts: int = 10) -> Optional[Coordinate]:
        """
        Вернет рандомную координату внутри комнаты, где ничего нет
        """
        for _ in range(max_attempts):
            rnd_crd: Coordinate = self._get_rnd_crd(room_id)
            if rnd_crd not in self.objects and rnd_crd not in self.mobs:
                return rnd_crd
        return None
    
    def _get_wall_point(self, room1: Room, room2: Room, room1_id: int, room2_id: int):
        """
        Определяет координаты комнат, где будет коридор
        """
        diff = room2_id - room1_id
        
        if abs(diff) == 1:  # Горизонтальный
            if diff > 0:  # Направо
                x1, x2 = room1.x_end, room2.x
            else:  # Налево
                x1, x2 = room1.x, room2.x_end
            y1 = randint(room1.y + 1, room1.y_end - 1)
            y2 = randint(room2.y + 1, room2.y_end - 1)
            
        else:  # Вертикальный 
            if diff > 0:  # Вниз
                y1, y2 = room1.y_end, room2.y
            else:  # Вверх
                y1, y2 = room1.y, room2.y_end
            x1 = randint(room1.x + 1, room1.x_end - 1)
            x2 = randint(room2.x + 1, room2.x_end - 1)
        
        return x1, y1, x2, y2

    def build_walkable(self):
        """
        Постпроение клеток, по которым можно ходить
        """
        for room in self.rooms:
            for y in range(room.y + 1, room.y_end):
                for x in range(room.x + 1, room.x_end):
                    self.walkable.add((y, x))
        for cor in self.corridors:
            for point in cor.points:
                self.walkable.add(point)
    
    def get_room_id_by_crd(self, crd: Coordinate) -> Optional[int]:
        """
        Возвращает id комнат по данными координатам
        """
        y, x = crd
        for i, room in enumerate(self.rooms):
            if room.y <= y <= room.y_end and room.x <= x <= room.x_end:
                return i
        return None
    
    def _place_exit_farthest_room(self, start_room_id: int) -> None:
        """
        Поиск самой далекой от игрока комнаты и размещение выхода в нем
        """
        graph = {i: [] for i in range(len(self.rooms))}
        for cor in self.corridors:
            graph[cor.room1_id].append(cor.room2_id)
            graph[cor.room2_id].append(cor.room1_id)
        
        queue = deque([start_room_id])
        dist = {start_room_id: 0}
        farthest_rooms = [start_room_id]
        max_dist = 0

        while queue:
            room_id = queue.popleft()
            current_dist = dist[room_id]

            if current_dist > max_dist:
                max_dist = current_dist
                farthest_rooms = [room_id]
            elif current_dist == max_dist:
                farthest_rooms.append(room_id)

            for neighbor in graph[room_id]:
                if neighbor not in dist:
                    dist[neighbor] = current_dist + 1
                    queue.append(neighbor)

        target_room_id = choice(farthest_rooms)
        target_room = self.rooms[target_room_id]

        for _ in range(3):
            y = randint(target_room.y + 1, target_room.y_end - 1)
            x = randint(target_room.x + 1, target_room.x_end - 1)
            if (y, x) not in self.objects and (y, x) not in self.mobs:
                self.exit = (y, x)
                return
        self.exit = (target_room.y + 1, target_room.x + 1)

    def _place_exit_with_player(self, start_room_id: int) -> None:
        """
        Тестовая функция для размещения выхода рядом с игроком
        """
        self.exit = self._get_rnd_free_crd(start_room_id)

    def is_walkable(self, y: int, x: int) -> bool:
        """
        Проверка на возможность перемещения игроком
        """
        return (y, x) in self.walkable
    
    def is_mob(self, y: int, x: int) -> bool:
        """
        Проверка на моба
        """
        return (y, x) in self.mobs
    
    def next_level(self) -> None:
        """
        Переход на следующий уровень
        """
        self.lvl += 1
        statistica.lvl = self.lvl
        self._clear_level()
        self._generate_level()
    
    def add_obj(self, item: Optional[Item], crd: Coordinate) -> bool:
        """
        Добавление предмета по координатам
        """
        if crd not in self.objects or self.objects[crd] is None:
            self.objects[crd] = item
            return True
        return False
    
    def get_event(self, crd: Coordinate) -> Optional[Union[Item, Enemy]]:
        """
        Вернет ивент по координатам
        """
        if crd in self.objects:
            return self.objects[crd]
        elif crd in self.mobs:
            return self.mobs[crd]
        return None
    
    def get_obj(self, crd: Coordinate) -> Optional[Item]:
        """
        Вернет предмет по координатам
        """
        if crd in self.objects:
            return self.objects[crd]
        return None
    
    def del_obj(self, crd: Coordinate) -> None:
        """
        Удаление предмета по координатам
        """
        if crd not in self.objects:
            return
        del self.objects[crd]
    
    def add_mob(self, item: Optional[Enemy], crd: Coordinate) -> bool:
        """
        Добавление моба по координатам
        """
        if crd not in self.mobs or self.mobs[crd] is None or self.objects[crd] is None:
            self.mobs[crd] = item
            return True
        return False
    
    def get_mob(self, crd: Coordinate) -> Optional[Enemy]:
        """
        Вернет моба по координатам
        """
        if crd not in self.mobs:
            return None
        return self.mobs[crd]
    
    def del_mob(self, crd: Coordinate) -> None:
        """
        Удаление моба по координатам
        """
        if crd not in self.mobs:
            return
        del self.mobs[crd]

    def load_level(self, data):
        """
        Загружает уровень из файла
        """
        self.lvl = data["lvl"]
        self.exit = tuple(data["exit"])
        self.rooms = data["rooms"]
        self.corridors = data["corridors"]
        self.doors = {coord: door for item in data["doors"] for coord, door in item.items()}
        self.mobs = {coord: enemy for item in data["enemies"] for coord, enemy in item.items()}
        self.objects = {coord: item for it in data["items"] for coord, item in it.items()}
        self.build_walkable()
        
    def test_spawn_items_in_start_room(self, count: int) -> None:
        """
        Генерирует указанное количество случайных предметов в стартовой комнате.
        Тестирование.
        """
        if self.start_room_id is None:
            return
        for _ in range(count):
            cell = self._get_rnd_free_crd(self.start_room_id)
            if cell is None:
                continue
            item = create_rnd_item(lvl=self.lvl, skill_lvl=player.skill_lvl)
            self.add_obj(item, cell)

    def check_player_harm(self) -> int:
        """
        Проверяет есть ли рядом мобы, высчитывает урон по игроку (с учетом попал или нет), если есть
        """
        y, x = player.crd
        harm = 0
        possible_mobs_crd = [(y, x + 1), (y, x - 1), (y + 1, x), (y - 1, x)]
        for crd in possible_mobs_crd:
            mob = self.get_mob(crd)
            if mob and mob.hit_player(player.dexterity):
                harm += mob.on_hit_player(player)

        return harm

    def kill_mob(self, crd: Coordinate) -> None:
        """
        Смерть монстра. Оставляет за собой золото
        """
        mob = self.get_mob(crd)
        gold = mob.health//2 + mob.strength + mob.dexterity + round(self.lvl * 1.5)

        treasure = Treasure(f"Сокровища {mob.name}", abs(gold))
        self.del_mob(crd)
        free_cell = self.find_free_space_around(crd)
        self.add_obj(treasure, free_cell)

    def find_free_space_around(self, crd: Coordinate) -> Coordinate:
        """
        Найти ближайшую пустую клетку от координат
        """
        if (crd not in self.objects and crd not in self.mobs and 
            self.is_walkable(crd[0], crd[1]) and crd != player.crd):
            return crd
        visited = set()
        queue = deque([crd])
        visited.add(crd)
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        
        while queue:
            y, x = queue.popleft()
            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if (ny, nx) in visited:
                    continue
                visited.add((ny, nx))
                if not self.is_walkable(ny, nx):
                    continue
                if (ny, nx) in self.objects or (ny, nx) in self.mobs \
                    or (ny, nx) == player.crd:
                    queue.append((ny, nx))
                else:
                    return (ny, nx)
    
    def move_mob(self, old_crd: Coordinate, new_crd: Coordinate) -> None:
        """
        Переместить моба
        """
        if old_crd == new_crd:
            return
        mob = self.mobs.get(old_crd)
        del self.mobs[old_crd]
        self.mobs[new_crd] = mob
    
    def move_mobs(self) -> None:
        """
        Проверка на агр и перемещение всех мобов
        """
        for old_crd, mob in list(self.mobs.items()):
            mob.check_engaged(old_crd, self)
            new_crd = mob.next_move(old_crd, self)
            self.move_mob(old_crd, new_crd)
    
    def drop_item(self, item: Item) -> None:
        """
        Выпадение предмета
        """
        free_crd = self.find_free_space_around(player.crd)
        if free_crd:
            self.add_obj(item, free_crd)

    def _generate_doors(self) -> None:
        """
        Генерация дверей
        """
        placed_doors = 0
        colors = list(DoorColor)
        while placed_doors < len(DoorColor):
            corridor = choice(self.corridors)
            id = randint(1, len(corridor.points) - 2)
            door_pos = corridor.points[id]

            color = choice(colors)
            colors.remove(color)

            door = Door(color, corridor.room1_id, corridor.room2_id)
            self.doors[door_pos] = door
            placed_doors += 1

    def _generate_keys(self) -> None:
        """
        Генерация ключей на основе расположения дверей и стартовой комнаты
        """
        graph = {i: [] for i in range(len(self.rooms))}
        for cor in self.corridors:
            graph[cor.room1_id].append(cor.room2_id)
            graph[cor.room2_id].append(cor.room1_id)
        
        for _, door in self.doors.items():
            visited = set()
            queue = deque([self.start_room_id])
            visited.add(self.start_room_id)
            
            while queue:
                room_id = queue.popleft()
                for neighbor in graph[room_id]:
                    if (room_id == door.room_a and neighbor == door.room_b) or \
                    (room_id == door.room_b and neighbor == door.room_a):
                        continue
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            room_id = choice(list(visited))
            cell = self._get_rnd_free_crd(room_id)
            key = Key(door.color_code)
            self.add_obj(key, cell)

    def is_door(self, y: int, x: int) -> bool:
        return (y, x) in self.doors
    
    def get_door_color(self, y: int, x: int) -> int:
        return self.doors[y, x].color
    
    def delete_door(self, y: int, x: int) -> None:
        del self.doors[y, x]