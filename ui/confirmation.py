import ui.window
import ui.widgets

def confirm(screen, message): # TODO: add a default parameter
    win = ui.window.Window(screen, margins=(68, 17))
    win.gen_window()
    win.gen_title(message)
    win.gen_widgets([(ui.widgets.ListItem, "Cancel", ""), (ui.widgets.ListItem, "Confirm", "")], confirm=False)
   
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
                win.widgets[win.cur_widget].active = False
                win.widgets[win.cur_widget].draw()
                win.cur_widget = response
        if response == "finish":
            finished = True
            win.delete()
            return win.cur_widget == 1