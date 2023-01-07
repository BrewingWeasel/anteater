def get_option(win):
    while True:
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
        if response == "escape":
            win.delete()
            return 0
        if response == "finish":
            win.delete()
            return win.cur_widget


def get_preview_option(options):
    cur_widget = 0
    while True:
        response = options[cur_widget].get_input()
        if response == "up":
            if cur_widget > 0:
                cur_widget -= 1
        if response == "down":
            if cur_widget < len(options) - 1:
                cur_widget += 1
        if response == "escape":
            return False
        if response == "finish":
            return cur_widget
