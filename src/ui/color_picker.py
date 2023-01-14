import ui.widgets
import ui.window
import ui.options

COLORS = ["white", "black", "red", "green",
          "yellow", "blue", "magenta", "aqua"]


def get_color(screen):
    win = ui.window.make_adaptive_window(
        screen,
        [(ui.widgets.ListItem, color, "", i)
         for i, color in enumerate(COLORS)],
        title="Pick your color",
        confirm=False,
    )

    return ui.options.get_option(win)
