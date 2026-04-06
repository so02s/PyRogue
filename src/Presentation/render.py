from abc import ABC, abstractmethod

class Renderer(ABC):
    def __init__(self, stdscr, level):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def draw_room(self, room):
        pass

    @abstractmethod
    def draw_coridor(self, corridor):
        pass

    @abstractmethod
    def draw_exit(self):
        pass

    @abstractmethod
    def draw_events(self):
        pass

    @abstractmethod
    def draw_character(self):
        pass

    @abstractmethod
    def draw_stats(self, y):
        pass