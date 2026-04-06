from Domain import SingletonMeta, player
from Domain.items import Item, Treasure
from typing import List, Optional
from Datalayer.statistica import statistica

class _Backpack(metaclass=SingletonMeta):
    categories = ['food', 'potion', 'scroll', 'weapon']

    def __init__(self):
        self._items = {}
        self.index: int = 0
        self.gold: int = 0
    
    def add_item(self, item: Item) -> bool:
        """
        Добавление предмета
        """
        if item is None:
            return False
        if isinstance(item, Treasure):
            item.pick_up(backpack)
            statistica.amount_of_treasure = self.gold
            return True
        if item.type not in self._items:
            self._items[item.type] = []
        if len(self._items[item.type]) < 9:
            self._items[item.type].append(item)
            item.pick_up()
            return True
        else:
            return False
    
    def del_item(self, item: Item) -> None:
        """
        Удаление предмета
        """
        if item.type not in self._items or \
            item not in self._items[item.type]:
            return
        self._items[item.type].remove(item)
        
        if not self._items[item.type]:
            del self._items[item.type]
            
        total = self.total_count()
        if total == 0:
            self.index = 0
        elif self.index >= total:
            self.index = total - 1
            
    def get_all_items(self) -> List:
        """
        Возвращает списком все предметы
        """
        all_items = []
        for cat in self.categories:
            if cat in self._items:
                all_items.extend(self._items[cat])
        return all_items
    
    def total_count(self) -> int:
        """
        Сколько всего предметов в рюкзаке
        """
        return len(self.get_all_items())
    
    def get_type_count(self, type: str) -> int:
        """
        Сколько предметов одного типа лежат в рюкзаке
        """
        return len(self._items[type]) if type in self._items else 0
    
    def get_type_list(self, type: str) -> Optional[List[Item]]:
        """
        Список предметов конкрутного типа
        """
        return self._items.get(type, [])

    def move_down(self) -> None:
        """
        Переместиться по списку ниже
        """
        total = self.total_count()
        if total > 0 and self.index < total - 1:
            self.index += 1
    
    def move_up(self) -> None:
        """
        Переместиться по списку выше
        """
        if self.index > 0:
            self.index -= 1


    def use_item(self, map):
        """
        Использовать выделенный предмет
        """
        all_items = self.get_all_items()
        if not all_items or self.index < 0 or self.index >= len(all_items):
            return
        item = all_items[self.index]
        ret_item = item.use(player)
        statistica.add_count_amount(item.type)
        self.del_item(item)
        if ret_item:
            map.drop_item(ret_item)
    
    def set_index_to_start(self) -> None:
        """
        Поставить индекс в начало
        """
        self.index = 0

    def clear(self) -> None:
        """
        Почистить рюкзак
        """
        self._items.clear()
        self.index = 0
        self.gold = 0
    
    def add_gold(self, points: int) -> None:
        """
        Добавить золото
        """
        self.gold += points
    
    def is_weapon_slot(self) -> bool:
        """
        Возвращает True, если текущий индекс указывает на слот оружия.
        """
        return self.index == self.total_count()
    
    def unequip_weapon(self, map) -> None:
        """
        Убрать в инвентарь оружие. Если места нет - выбросить 
        """
        if self.get_type_count("weapon") == 9:
            map.drop_item(player.add_weapon(None))
        else:
            backpack.add_item(player.add_weapon(None))
    
    def has_key(self, color: int) -> bool:
        """
        Есть ли ключ такого цвета
        """
        keys = self.get_type_list('key')
        if keys:
            colors = [key.color for key in keys]
            if color in colors:
                return True
        return False
    
    def del_key(self, color: int) -> None:
        """
        Удаление ключа по цвету
        """
        keys = self.get_type_list('key')
        for key in keys:
            if key.color == color:
                self.del_item(key)
    
    def del_keys(self) -> None:
        """
        Удаление всех ключей
        """
        keys = self.get_type_list('key')
        for key in keys:
            self.del_item(key)

backpack = _Backpack()