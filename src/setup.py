import shutil
import os
import curses

USER_DIR = os.path.expanduser("~")
CONFIG_DIR = os.path.join(USER_DIR, ".config/anteater/")


def make_brushes():
    brushes_dir = os.path.join(CONFIG_DIR, "brushes")
    if not os.path.exists(brushes_dir):
        os.makedirs(brushes_dir)
        for brush in os.listdir("brushes"):
            shutil.copy(f"brushes/{brush}", f"{brushes_dir}/{brush}")


def curses_settings():
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    curses.init_pair(25, 7, 2)
    curses.init_pair(26, 7, 4)
    curses.init_pair(27, 2, 4)
    curses.init_pair(28, 4, 2)
    curses.init_pair(29, 7, 5)
    curses.init_pair(30, 5, 2)

    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS |
                     curses.REPORT_MOUSE_POSITION)
    curses.flushinp()
    curses.noecho()


def main():
    make_brushes()
    curses_settings()
    # TODO Add more setup and config options


if __name__ == "__main__":
    main()
