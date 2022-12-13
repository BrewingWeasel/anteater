import ui.window
import ui.widgets
import ui.options
import math
import curses


def show_help(screen):
    win = ui.window.Window(screen, margins=(40, 12))
    win.gen_window()
    win.gen_title("Keyboard Shortcuts")

    shortcut_info = [
        "right arrow: next frame",
        "left arrow: last frame",
        "d: enter draw mode",
        "e: enter erase mode",
        "r: reset mode",
        "l: clear current frame",
        "o: export animation",
        "z: undo",
        "Z: redo",
        "c: change character",
        "s: change color",
        "S: save file",
        "i: import  file",
        "y: copy",
        "p: paste",
        "ctrl + a: select all",
        "ctrl + d: deselect",
        "h: show this menu",
    ]
    for i, info in enumerate(shortcut_info):
        win.gen_text(info, ypos=2 + math.floor(i / 2), xpos=3 + 40 * (i % 2))

    win.gen_text(
        "Press any key to hide this menu",
        ypos=4 + math.floor(len(shortcut_info) / 2),
        style=curses.A_BOLD,
    )
    screen.getch()
    win.delete()
