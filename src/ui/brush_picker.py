import ui.widgets
import ui.window
import ui.options
import os
BRUSHES = os.listdir("brushes")


def get_brush(screen):
    win = ui.window.Window(screen, margins=(70, 14))
    win.gen_window()
    win.gen_title("Pick your color")
    win.gen_widgets(
        [(ui.widgets.ListItem, brush, "")
         for brush in BRUSHES],
        confirm=False
    )

    return BRUSHES[ui.options.get_option(win)]

