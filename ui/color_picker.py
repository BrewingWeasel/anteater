import ui.widgets
import ui.window

COLORS = ["white", "black", "red", "green", "yellow", "blue", "magenta", "aqua"]


def get_color(screen):
    win = ui.window.Window(screen, margins=(4, 10))
    win.gen_window()
    win.gen_title("Pick your color")
    win.gen_widgets(
        [(ui.widgets.ListItem, color, "") for color in COLORS], confirm=False
    )

    finished = False
    while not finished:
        response = win.widgets[win.cur_widget].get_input()
        if response == "up":
            win.cur_widget -= 1 if win.cur_widget > 0 else 0
        if response == "down":
            if win.cur_widget < len(win.widgets) - 1:
                win.cur_widget += 1
        if isinstance(response, int):
            if response < len(win.widgets) and response >= 0:
                win.cur_widget = response
        if response == "finish":
            finished = True
            win.delete()
            return win.cur_widget
