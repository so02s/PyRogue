import os
import json
from Domain.map.level import Level
from Domain.map.room import Room
from Domain.map.coridor import Coridor
from Domain import player, backpack
from Domain.items import Item, factory
from Domain.items.weapon import Weapon
from Domain.enemies import Enemy
from Domain.enemies.mimik import Mimic
from Domain.stat_util import StatType
from .statistica import statistica
from Domain.map.key import Key
from Domain.map.door import DoorColor, Door

class datalayer:
    def __init__(self, level):
        self.file_for_save = "Datalayer/progress.json"
        self.file_for_statistica = "Datalayer/statistica.json"
        self.map = level

    def check_file(self, name_file):
        if not os.path.exists(name_file):
            with open(name_file, 'w') as file:
                json.dump([], file)

    def add_information(self):
        self.check_file(self.file_for_save)
        
        data = {"lvl": 1}
        with open(self.file_for_save, 'r') as file:
            load_data = json.load(file)

        data["lvl"] = self.map.lvl
        data["exit"] = self.map.exit

        statistica_info = statistica.statistica_to_dict()

        player_info = {
            "effects": {k.name: list(v) for k, v in player._effects.items()},
            "base_strength": player.base_strength,
            "base_dexterity": player.base_dexterity,
            "base_health": player.base_health,
            "current_health": player.current_health,
            "x": player.x,
            "y":player.y,
            "skill_lvl": player.skill_lvl,
            "weapon": player.weapon._base_name if player.weapon else None
        }

        backpack_items = []
        for category, items_list in backpack._items.items():
            for item in items_list:
                item_dict = {
                    "cls": type(item).__name__,
                    "category": category
                }
                if type(item).__name__ == "Treasure" or type(item).__name__ == "Scroll":
                    item_dict["sub_class"] = item._base_name
                    item_dict["value"] = item.value
                elif type(item).__name__ == "Key":
                    item_dict["color"] = item.color
                else:
                    item_dict["sub_class"] = item._base_name
                backpack_items.append(item_dict)

        backpack_info = {
            "items": backpack_items,
            "index": backpack.index,
            "gold": backpack.gold
        }

        corridors_list = []
        for one_corridor in self.map.corridors:
            one_corridor_dict = {
                "room_x1": one_corridor.room_x1,
                "room_y1": one_corridor.room_y1,
                "room_x2": one_corridor.room_x2,
                "room_y2": one_corridor.room_y2,
                "room1_id": one_corridor.room1_id,
                "room2_id": one_corridor.room2_id,
                "points": one_corridor.points,
                "visitable": one_corridor.visitable,
                "enter": one_corridor.enter
            }
            corridors_list.append(one_corridor_dict)

        rooms_list = []
        for one_room in self.map.rooms:
            one_room_dict = {
                "x": one_room.x,
                "y": one_room.y,
                "x_end": one_room.x_end,
                "y_end": one_room.y_end,
                "height": one_room.height,
                "width": one_room.width,
                "id": one_room.id,
                "visited": one_room.visited,
            }
            rooms_list.append(one_room_dict)

        enemy_list = []
        for coord, enemy in self.map.mobs.items():
            one_enemy = {
                "coordinate": list(coord),
                "health" : enemy.health,
                "dexterity" : enemy.dexterity,
                "strength" : enemy.strength,
                "level" : enemy.level
            }
            enemy_type = enemy.get_type()
            if enemy_type not in enemy._enemy_attr:
                one_enemy["name"] = 'm'
                one_enemy["symbol"] = enemy.actual_symb
                one_enemy["color"] = enemy.actual_color
            else:
                one_enemy["name"] = enemy_type
            enemy_list.append(one_enemy)

        doors_list = []
        for coord, door in self.map.doors.items():
            one_door = {
                "coordinate": list(coord),
                "color": door.color,
                "locked": door.locked
            }
            doors_list.append(one_door)

        items_list = []
        for coord, item in self.map.objects.items():
            one_item = {
                "coordinate": list(coord),
                "cls": type(item).__name__,
            }
            if type(item).__name__ == "Treasure" or type(item).__name__ == "Scroll":
                one_item["sub_class"] = item._base_name
                one_item["value"] = item.value
            elif type(item).__name__ == "Key":
                one_item["color"] = item.color
            else:
                one_item["sub_class"] = item._base_name
            items_list.append(one_item)

        data["statistica"] = statistica_info
        data["player"] = player_info
        data["backpack"] = backpack_info
        data["corridors"] = corridors_list
        data["rooms"] = rooms_list
        data["doors"] = doors_list
        data["enemies"] = enemy_list
        data["items"] = items_list

        load_data.append(data)
        
        with open(self.file_for_save, 'w') as file:
            json.dump(load_data, file, indent=2)

    def load_last_game(self):
        if not os.path.exists(self.file_for_save):
            return {}

        with open(self.file_for_save, 'r') as file:
            load_data = json.load(file)

        CLASS_BY_NAME = {cls.__name__: cls for cls in factory._ITEM_TYPE_DATA.keys()}
        CLASS_BY_NAME["Key"] = Key
        load_data = load_data[-1]
        data = {
                "lvl" : load_data["lvl"],
                "exit" : load_data["exit"]
                }
        
        statistica_data = load_data["statistica"]
        statistica.amount_of_treasure = statistica_data["amount_of_treasure"]
        statistica.lvl = statistica_data["lvl"]
        statistica.number_of_enemies = statistica_data["number_of_enemies"]
        statistica.amount_of_food = statistica_data["amount_of_food"]
        statistica.number_of_elixirs = statistica_data["number_of_elixirs"]
        statistica.number_of_scrolls = statistica_data["number_of_scrolls"]
        statistica.number_of_attacks_made = statistica_data["number_of_attacks_made"]
        statistica.number_of_attacks_hits = statistica_data["number_of_attacks_hits"]
        statistica.number_of_tiles = statistica_data["number_of_tiles"]

        player_data = load_data["player"]
        if "effects" in player_data:
            player._effects = {StatType[k]: tuple(v) for k, v in player_data["effects"].items()}
        else:
            player._effects = {}
        player.base_strength = player_data["base_strength"]
        player.base_dexterity = player_data["base_dexterity"]
        player.base_health = player_data["base_health"]
        player.current_health = player_data["current_health"]
        player.x = player_data["x"]
        player.y = player_data["y"]
        player.skill_lvl = player_data["skill_lvl"]
        if player_data["weapon"]:
            player.weapon = Weapon(player_data["weapon"])

        backpack_data = load_data["backpack"]
        
        backpack._items = {}
        for item_data in backpack_data["items"]:
            class_name = item_data["cls"]
            category = item_data["category"]
            item_class = CLASS_BY_NAME[class_name]
            if class_name == "Treasure" or class_name == "Scroll":
                item = item_class(name=item_data["sub_class"], value=item_data["value"])
            elif class_name == "Key":
                item  = item_class(color=DoorColor(item_data["color"]))
            else:
                item = item_class(name=item_data["sub_class"])
            if category not in backpack._items:
                backpack._items[category] = []
            backpack._items[category].append(item)

        backpack.index = backpack_data["index"]
        backpack.gold = backpack_data["gold"]

        rooms = []
        for room_dict in load_data["rooms"]:
            room = Room(
                start_x=room_dict["x"],
                start_y=room_dict["y"],
                height=room_dict["height"],
                width=room_dict["width"],
                id=room_dict["id"]
            )
            room.visited = room_dict.get("visited")
            rooms.append(room)

        corridors = []
        for corr_dict in load_data["corridors"]:
            corridor = Coridor(
                room_x1=corr_dict["room_x1"],
                room_y1=corr_dict["room_y1"],
                room_x2=corr_dict["room_x2"],
                room_y2=corr_dict["room_y2"],
                room1_id=corr_dict["room1_id"],
                room2_id=corr_dict["room2_id"],
                enter=corr_dict["enter"]
            )
            corridor.points = [tuple(p) for p in corr_dict.get("points", [])]
            corridor.visitable = corr_dict.get("visitable")
            corridors.append(corridor)

        doors = []
        for door in load_data["doors"]:
            y, x = door["coordinate"]
            one_door = Door(DoorColor(door["color"]), locked=door["locked"])
            doors.append({(y, x) : one_door})


        enemies = []
        for enemy in load_data["enemies"]:
            y, x = enemy["coordinate"]
            if enemy["name"] == 'm':
                mimic = Mimic(
                    level=enemy["level"],
                    actual_symb=enemy["symbol"],
                    actual_color=enemy["color"]
                )
                mimic.health = enemy["health"]
                mimic.dexterity = enemy["dexterity"]
                mimic.strength = enemy["strength"]
                enemy_obj = mimic
            else:
                enemy_obj = Enemy(
                    health=enemy["health"],
                    dexterity=enemy["dexterity"],
                    strength=enemy["strength"],
                    type=enemy["name"],
                    level=enemy["level"]
                )
            enemies.append({(y, x) : enemy_obj})
        
        items = []
        for item in load_data["items"]:
            y, x = item["coordinate"]
            class_name = item["cls"]
            item_class = CLASS_BY_NAME[class_name]
            if class_name == "Treasure" or class_name == "Scroll":
                it = item_class(name=item["sub_class"], value=item["value"])
            elif class_name == "Key":
                it = item_class(color=DoorColor(item["color"]))
            else:
                it = item_class(name=item["sub_class"])
            items.append({(y, x) : it})

        data["rooms"] = rooms
        data["corridors"] = corridors
        data["doors"] = doors
        data["enemies"] = enemies
        data["items"] = items

        return data

    def delete_progress(self):
        if os.path.exists(self.file_for_save):
            os.remove(self.file_for_save)

        


    


        