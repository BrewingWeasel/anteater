import ui.window
import ui.widgets
import ui.options
import os

usrdir = os.path.expanduser("~")
save_path = os.path.join(usrdir, ".local", "share", "anteater")
TITLE = "Pick your project"


def start_window(screen):
    widgets = []
    if os.path.isdir(save_path):
        for project in os.listdir(save_path):
            widgets.append((ui.widgets.ListItem, project, ""))

    max_size = len(TITLE)
    for i in widgets:
        maxSize = max(len(i[1]), max_size)

    win = ui.window.Window(
        screen,
        size=(maxSize + 5, len(widgets) + 5),
    )
    win.gen_window()
    win.gen_title(TITLE)
    win.widgets.append(
        ui.widgets.ListItem(screen, win.ymargin + 2,
                            win.xmargin + 4, "New project")
    )

    # Use for project text (TODO does this actually look better/more readable?)
    # win.gen_text("PROJECTS", ypos=4, style=curses.A_BOLD | curses.A_UNDERLINE)

    win.gen_widgets(widgets, confirm=False, offset=5)

    response = ui.options.get_option(win)
    if response != 0:
        return os.listdir(save_path)[response - 1]
    return "new"
