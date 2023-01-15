import ui.window
import ui.widgets
import ui.options


def confirm(screen, message):  # TODO: add a default parameter
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
