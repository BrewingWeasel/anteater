import ui.widgets
import ui.window
import ui.options
import os
BRUSHES = os.listdir("brushes")


def get_brush(screen):
    margins = (20, 10)
    win = ui.window.Window(screen, margins=margins)
    win.gen_window()
    win.gen_title("Choose a brush")

    options = []
    for brush_num, brush in enumerate(BRUSHES):
        with open(f'brushes/{brush}', 'r') as f:
            brush_shape = f.read().split("#SIZE\n")[3].replace("*", "A")
            options.append(ui.widgets.PreviewListItem(
                screen, 20, margins[0] + 5 + (brush_num % 4) * 24, brush_shape, brush))

    response = BRUSHES[ui.options.get_preview_option(options)]
    win.delete()
    return response
