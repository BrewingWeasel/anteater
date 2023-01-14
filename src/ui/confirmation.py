import ui.window
import ui.widgets
import ui.options


def confirm(screen, message):  # TODO: add a default parameter
    # win = ui.window.Window(screen, margins=(68, 17), size=(2, 10))
    # win.gen_window()
    # win.gen_title(message)
    # win.gen_widgets(
    #     [(ui.widgets.ListItem, "Cancel", ""),
    #      (ui.widgets.ListItem, "Confirm", "")],
    #     confirm=False,
    # )
    win = ui.window.make_adaptive_window(
        screen,
        title=message,
        widgets=[
            (ui.widgets.ListItem, "Cancel", ""),
            (ui.widgets.ListItem, "Confirm", ""),
        ],
        confirm=False,
    )

    return ui.options.get_option(win)
