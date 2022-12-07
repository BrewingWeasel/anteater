import ui.window
import ui.widgets
import ui.options

def confirm(screen, message): # TODO: add a default parameter
    win = ui.window.Window(screen, margins=(68, 17))
    win.gen_window()
    win.gen_title(message)
    win.gen_widgets([(ui.widgets.ListItem, "Cancel", ""), (ui.widgets.ListItem, "Confirm", "")], confirm=False)
   
    finished = False
    return ui.options.get_option(win)