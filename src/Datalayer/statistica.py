from Domain.singletone_wrapper import SingletonMeta
import os
import json

class _Statistica(metaclass=SingletonMeta):
    def __init__(self):
        self.file_for_statistica = "Datalayer/statistica.json"
        self.amount_of_treasure = 0
        self.lvl = 1
        self.number_of_enemies = 0
        self.amount_of_food = 0
        self.number_of_elixirs = 0
        self.number_of_scrolls = 0
        self.number_of_attacks_made = 0
        self.number_of_attacks_hits = 0
        self.number_of_tiles = 0

        self.select_index = 0
        self.full_statistica = {}

    def add_count_amount(self, item_type):
        if item_type == "food":
            self.amount_of_food += 1
        elif item_type == "potion":
            self.number_of_elixirs += 1
        elif item_type == "scroll":
            self.number_of_scrolls += 1   

    def update_statistica(self):
        statistica_list = []
        if not os.path.exists(self.file_for_statistica):
            with open(self.file_for_statistica, 'w') as file:
                json.dump([], file)
        else:
            with open(self.file_for_statistica, 'r') as file:
                statistica_list = json.load(file)

        new_statistica_dict = self.statistica_to_dict()
        statistica_list.append(new_statistica_dict)

        with open(self.file_for_statistica, 'w') as file:
            json.dump(statistica_list, file, indent=2)

    def statistica_sort(self) -> dict:
        if os.path.exists(self.file_for_statistica):
            with open(self.file_for_statistica, 'r') as file:
                statistica_list = json.load(file)
            statistica_list.sort(key=lambda x: x["amount_of_treasure"], reverse=True)
            self.full_statistica = statistica_list

    def next(self) -> None:
        if self.select_index < len(self.full_statistica) - 1:
            self.select_index += 1
    
    def prev(self) -> None:
        if self.select_index > 0:
            self.select_index -= 1

    def statistica_to_dict(self):
        new_statistica_dict = {
            "amount_of_treasure" : self.amount_of_treasure,
            "lvl" : self.lvl,
            "number_of_enemies" : self.number_of_enemies,
            "amount_of_food" : self.amount_of_food,
            "number_of_elixirs" : self.number_of_elixirs,
            "number_of_scrolls" : self.number_of_scrolls,
            "number_of_attacks_made" : self.number_of_attacks_made,
            "number_of_attacks_hits" : self.number_of_attacks_hits,
            "number_of_tiles" : self.number_of_tiles
        }
        return new_statistica_dict

statistica = _Statistica()
statistica.statistica_sort()
        