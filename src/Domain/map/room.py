# from Domain import Coordinate
# from typing import Any
# from Domain.enemies.enemy import Enemy

class Room():
    def __init__(self, start_x: int, start_y: int, height: int, width: int, id: int) -> None:
        """
        x, y - координаты первой точки
        height - высота комнаты
        width - длинна комнаты
        x_end, y_end - координаты последней точки
        """
        
        self.x, self.y, self.x_end, self.y_end = start_x, start_y, start_x + width - 1, start_y + height - 1
        self.height = height
        self.width = width
        self.id = id

        # self.objects: dict[Coordinate, Any] = {}
        # self.enemies: list[Enemy] = []
        self.visited: bool = False

    # def add_event(self, crd: Coordinate, obj: Any) -> None:
    #     self.objects[crd] = obj
    
    # def del_obj(self, crd: Coordinate) -> None:
    #     self.objects[crd] = None
    
    # def add_enemy(self, enemy: Enemy) -> None:
    #     # при генерации обязательно учитывать наложение монстров и предметов!
    #     # потом, при перемещении они будут проверять столкновения
    #     self.enemies.append(enemy)
        
    # def del_enemy(self, enemy: Enemy) -> None:
    #     self.enemies.remove(enemy)

    # def get_cell(self, crd: Coordinate) -> Any:
    #     """Возвращает любую штуку по координатам"""
    #     if crd in self.objects and self.objects[crd] is not None:
    #         return self.objects[crd]
    #     return None
    
    # def check_collision(self, char_crd: Coordinate, d_crd: Coordinate) -> Coordinate:
    #     if char_crd[0] + d_crd[0] >= self.y_end or \
    #        char_crd[0] + d_crd[0] <= self.y:
    #         dy = 0
    #     else:
    #         dy = d_crd[0]
    #     if char_crd[1] + d_crd[1] >= self.x_end or \
    #        char_crd[1] + d_crd[1] <= self.x:
    #         dx = 0
    #     else:
    #         dx = d_crd[1]
    #     return dy, dx
    
    # def move_mobs(self):
    #     for enemy in self.enemies:
    #         crd: Coordinate = enemy.next_move([])
    #         enemy.move(crd)
