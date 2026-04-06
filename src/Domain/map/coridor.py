import random

class Coridor():
    def __init__(self, room_x1: int, room_y1: int, room_x2: int, room_y2: int, room1_id: int, room2_id: int, points: list = None, visitable: bool = None, enter: int = None) -> None:
        """        
        room_x1, room_y1 х и у комнаты откуда выходит коридор
        room_x2, room_y2 х и у комнаты куда входит коридор
        room1_id, room2_id - id комнат для определения направления
        points - точки коридора
        """
        self.room_x1 = room_x1
        self.room_y1 = room_y1
        self.room_x2 = room_x2
        self.room_y2 = room_y2
        self.room1_id = room1_id
        self.room2_id = room2_id
        self.points = []
        self.visitable = False
        self.enter = enter
        
    def generate_points(self) -> None:
        min_x, max_x = min(self.room_x1, self.room_x2), max(self.room_x1, self.room_x2)
        min_y, max_y = min(self.room_y1, self.room_y2), max(self.room_y1, self.room_y2)
        
        if abs(self.room1_id - self.room2_id) == 1:  # Горизонтальный 
            shift = random.randint(min_x + 1, max_x - 1) 
            for x in range(min_x, shift):
                self.points.append((self.room_y1, x))
            for y in range(min_y, max_y + 1):
                self.points.append((y, shift))
            for x in range(shift, max_x):
                self.points.append((self.room_y2, x + 1))
                
        else: # Вертикальный
            shift = random.randint(min_y + 1, max_y - 1)
            for y in range(min_y, shift):
                self.points.append((y, self.room_x1))
            for x in range(min_x, max_x + 1):
                self.points.append((shift, x))
            for y in range(shift, max_y + 1):
                self.points.append((y, self.room_x2))

        self.points = list(dict.fromkeys(self.points))
