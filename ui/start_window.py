import ui.window
import ui.widgets
import ui.options
import os

usrdir = os.path.expanduser("~")
save_path = os.path.join(usrdir, ".local", "share", "anteater")

def start_window(screen):
    win = ui.window.Window(screen)
    win.gen_window()
    win.gen_title("Pick your project")
    widgets = [(ui.widgets.ListItem, "New project", "")]
    if os.path.isdir(save_path):
        widgets += [(str, "_______________", ""), (str, "Projects", ""), (str, "_______________", "")]
        for project in os.listdir(save_path):
            widgets.append((ui.widgets.ListItem, project, ""))
    win.gen_widgets(widgets, confirm=False)
    
    response = ui.options.get_option(win)
    if response != 0:
        return os.listdir(save_path)[response - 1]
    return "new"