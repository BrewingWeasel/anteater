import ui.widgets
import ui.window
import ui.options

COLORS = ["white", "black", "red", "green", "yellow", "blue", "magenta", "aqua"]


def get_color(screen):
    win = ui.window.Window(screen, margins=(50, 13))
    win.gen_window()
    win.gen_title("Pick your color")
    win.gen_widgets(
        [(ui.widgets.ListItem, color, "") for color in COLORS], confirm=False
    )

    return ui.options.get_option(win)
