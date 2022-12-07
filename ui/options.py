def get_option(win):
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
        if response == "escape":
            win.delete()
            return 0
        if response == "finish":
            win.delete()
            return win.cur_widget