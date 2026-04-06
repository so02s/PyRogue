import curses
from Controller.controller import Controller

def main(stdscr):
    contr = Controller(stdscr)
    contr.start()

if __name__ == "__main__":
    curses.wrapper(main)