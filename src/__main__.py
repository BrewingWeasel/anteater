# USE export TERM=xterm-1003
import os
import sys
import curses
import traceback
import logging
import setup
from setup import CONFIG_DIR
import ui.window
import ui.color_picker
import ui.brush_picker
import ui.confirmation
import ui.start_window
import ui.help_menu
import ui.options
from drawing import Drawing


def main(stdscr):
    sys.setrecursionlimit(10000)  # Used for fill
    logging.basicConfig(filename="anteater.log",
                        encoding="utf-8", level=logging.DEBUG)
    setup.main()

    project = ui.start_window.start_window(stdscr)

    if project == "new":
        win = ui.window.Window(stdscr)

        win.gen_window()
        win.gen_title("new animation")
        win.widgets.append(
            ui.widgets.MultipleChoiceInline(
                win.screen,
                win.ymargin + 2,
                win.xmargin + 5,
                "Project type: ",
                ["drawing", "animation", "brush"],
            )
        )
        win.gen_widgets(
            [
                (ui.widgets.TextInput, "file name", "animation"),
                (ui.widgets.NumberInput, "total frames", "24"),
                (ui.widgets.NumberInput, "frames per second", "12"),
            ], offset=3
        )
        project_type, name, frames, fps, _ = win.get_contents()

        drawing = Drawing(
            project_name=name, frames=int(frames), fps=int(fps)
        )
        if project_type == "brush":
            drawing.export_file = f"{CONFIG_DIR}brushes/{drawing.project_name}"
            drawing.char = "*"
        if project_type == "drawing":
            drawing.frames = 1
            drawing.fps = 1

    else:
        drawing = Drawing()
        drawing.load(os.path.join(drawing.save_path, project))

    drawing.show_help()

    while drawing.running:
        try:
            drawing.display_top()
            drawing.get_keys()
        except KeyboardInterrupt:
            break  # Instead of the ugly error message
        except Exception as e:
            logging.error(traceback.format_exc())


curses.wrapper(main)
