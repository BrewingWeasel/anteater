import ui.widgets
import ui.window
import ui.options
import math
import os


BRUSHES = os.listdir("brushes")
BRUSHES_PER_ROW = 6


def get_brush(screen):
    margins = (20, 10)
    win = ui.window.Window(screen, margins=margins)
    win.gen_window()
    win.gen_title("Choose a brush")

    options = []
    cur_row = 0
    cur_widget = 0
    cur_row_changed = True
    while True:
        if cur_row_changed:
            win.gen_window()
            options = []
            for brush_num, brush in enumerate(BRUSHES):
                if math.floor(brush_num / BRUSHES_PER_ROW) == cur_row:
                    with open(f"brushes/{brush}", "r") as f:
                        brush_shape = f.read().split("#SIZE\n")[
                            3].replace("*", "A")
                        options.append(
                            ui.widgets.PreviewListItem(
                                screen,
                                20,
                                margins[0] + 5 + (brush_num %
                                                  BRUSHES_PER_ROW) * 24,
                                brush_shape,
                                brush,
                            )
                        )
            cur_row_changed = False

        # Get the input from the selected widget
        response = options[cur_widget].get_input()
        if response == "left":
            if cur_widget > 0:
                cur_widget -= 1
        elif response == "right":
            if cur_widget < len(options) - 1:
                cur_widget += 1
        elif response == "up":
            if cur_row > 0:
                cur_row -= 1
                cur_row_changed = True
        elif response == "down":
            if cur_row < (len(BRUSHES) / BRUSHES_PER_ROW) - 1:  # Why -2?
                cur_row += 1
                cur_row_changed = True
                if cur_widget + (cur_row * BRUSHES_PER_ROW) + cur_row > len(BRUSHES):
                    cur_widget = 0
        elif response == "escape":
            win.delete()
            return "default"
        elif response == "finish":
            win.delete()
            return BRUSHES[cur_row * BRUSHES_PER_ROW + cur_widget]
