# USE export TERM=xterm-1003
import os
import sys
import curses
import time
import traceback
import logging
import pickle
import setup
import export
from setup import CONFIG_DIR, USER_DIR
import ui.window
import ui.color_picker
import ui.brush_picker
import ui.confirmation
import ui.start_window
import ui.help_menu
import ui.options
import curve_detection


class Drawing:
    def __init__(self, frames=12, fps=12, project_name="animation"):
        # Initialize curses screen
        self.screen = curses.initscr()

        # Set up colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        curses.init_pair(25, 7, 2)
        curses.init_pair(26, 7, 4)
        curses.init_pair(27, 2, 4)
        curses.init_pair(28, 4, 2)
        curses.init_pair(29, 7, 5)
        curses.init_pair(30, 5, 2)

        self.screen.keypad(1)
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS |
                         curses.REPORT_MOUSE_POSITION)
        curses.flushinp()
        curses.noecho()

        self.usrdir = os.path.expanduser("~")
        self.save_path = os.path.join(
            self.usrdir, ".local", "share", "anteater")
        self.brush_dir = os.path.join(
            self.usrdir, ".config", "anteater", "brushes")

        self.frames = frames
        self.fps = fps
        self.project_name = project_name
        self.export_file = f"{project_name}.py"

        self.cur_frame = 0
        self.playing = False
        self.running = True
        self.draw = True
        self.erase = False
        self.fill = False
        self.modify = False
        self.selecting = False
        self.init_coords = None
        self.final_coords = None
        self.times_modified = 0
        self.buffer = []

        self.brush_size = 0
        self.brush = "default"
        self.get_cur_brush()

        self.char = "/"
        self.color = curses.COLOR_WHITE
        self.mode = "none"

        self.curve_mode = False

        self.charlocations = []
        for _ in range(self.frames):
            framelocations = []
            for _ in range(curses.LINES):
                framelocations.append([(" ", self.color)] * curses.COLS)
            self.charlocations.append(framelocations)

        self.history = [[]]
        self.recentlyadded = set()

        self.screen.clear()

    def in_selection(self, y, x):
        if self.final_coords is None:
            return True
        elif (
            self.final_coords[0] > y >= self.init_coords[0]
            and self.final_coords[1] >= x >= self.init_coords[1]
        ):
            return True
        return False

    def add_to_history(self):
        for character in self.recentlyadded:
            y, x, char = character
            oldchar, oldcolor = self.charlocations[self.cur_frame][y][x]
            self.charlocations[self.cur_frame][y][x] = (char, self.color)
            self.history[self.times_modified].append(
                (y, x, oldchar, char, oldcolor, self.color)
            )
        self.recentlyadded = set()

    def add_char(self, y, x, char_to_add="cur_char"):
        if char_to_add == "cur_char":
            char_to_add = self.char
        self.modifying_char = char_to_add
        try:
            if y > 0 and self.in_selection(y, x):
                self.screen.addstr(y, x, char_to_add, self.color)
                self.recentlyadded.add((y, x, char_to_add))
        except curses.error:
            logging.warning(
                f"Attempting to draw character outside of bounds at y: {y} x: {x}"
            )

    def unmodify(self):
        self.modify = False
        self.add_to_history()
        self.times_modified += 1
        self.history.append([])
        self.draw_selection()

    def react_to_mouse(self):
        _, x, y, _, button = curses.getmouse()
        if self.modify:
            if self.draw:
                self.draw_brush(y, x)
            if self.erase:
                self.add_char(y, x, char_to_add=" ")
        if button & curses.BUTTON1_PRESSED:
            self.modify = True
            if self.fill:
                self.draw_fill(y, x)
        elif button & curses.BUTTON1_CLICKED:
            if not self.modify:
                if self.draw:
                    self.draw_brush(y, x)
                if self.erase:
                    self.add_char(y, x, char_to_add=" ")
            self.unmodify()
        elif button & curses.BUTTON1_RELEASED:
            self.unmodify()
        elif button & curses.BUTTON3_PRESSED:
            if not self.selecting:
                self.remove_selection()
                self.init_coords = (y, x)
            self.selecting = True
        elif (
            button & curses.BUTTON3_RELEASED
            or button & curses.BUTTON3_PRESSED & self.selecting
        ):
            self.selecting = False
            self.final_coords = (y, x)
            # Make init coords be in the top left
            if self.final_coords is not None and self.init_coords is not None:
                if self.init_coords[0] > self.final_coords[0]:
                    self.final_coords, self.init_coords = (
                        self.init_coords[0],
                        self.final_coords[1],
                    ), (self.final_coords[0], self.init_coords[1])
                if self.init_coords[1] > self.final_coords[1]:
                    self.final_coords, self.init_coords = (
                        self.final_coords[0],
                        self.init_coords[1],
                    ), (self.init_coords[0], self.final_coords[1])

            self.draw_selection()

    def draw_brush(self, y, x):
        brush_lines = self.brush_shape.split("\n")
        brush_height = len(brush_lines)
        brush_width = len(max(brush_lines, key=len))
        draw_char = self.char
        if self.curve_mode:
            self.curve_detector((y, x))
            draw_char = self.curve_detector.get_char()

        for cy, line in enumerate(brush_lines):
            for cx, char in enumerate(line):
                if char == "*":
                    self.add_char(
                        y - round(brush_height / 2) + cy,
                        x - round(brush_width / 2) + cx,
                        char_to_add=draw_char,
                    )
                elif char != " ":
                    self.add_char(
                        y - round(brush_height / 2) + cy,
                        x - round(brush_width / 2) + cx,
                        char_to_add=char,
                    )

    def toggle_draw(self):
        self.toggle_modify()
        self.draw = True

    def toggle_erase(self):
        self.toggle_modify()
        self.erase = True

    def toggle_fill(self):
        self.toggle_modify()
        self.fill = True

    def toggle_modify(self):
        if self.modify:
            self.unmodify()
        else:
            self.draw = False
            self.erase = False
            self.fill = False

    def toggle_curve_mode(self):
        self.curve_mode = not self.curve_mode
        if self.curve_mode:
            self.curve_detector = curve_detection.Curve()

    def change_char(self):
        win = ui.window.Window(self.screen, margins=(40, 15))
        win.gen_window()
        win.gen_title("Change key")
        win.gen_text("Press key to change to")
        self.char = self.screen.getkey()
        while self.char.startswith("KEY"):
            self.char = self.screen.getkey()
        win.delete()
        self.draw_frame()
        self.reset_colors()

    def undo(self):
        if self.modify:
            self.unmodify()
        try:
            if len(self.history[self.times_modified - 1]):
                for i in self.history[self.times_modified - 1]:
                    y, x, oldchar, _newchar, oldcolor, _newcolor = i
                    try:
                        self.screen.addstr(y, x, oldchar, oldcolor)
                        self.charlocations[self.cur_frame][y][x] = (
                            oldchar, oldcolor)
                    except curses.error:
                        pass
                self.times_modified -= 1
        except IndexError:
            pass

    def redo(self):
        try:
            if len(self.history[self.times_modified]):
                for i in self.history[self.times_modified]:
                    y, x, _, newchar, _, newcolor = i
                    try:
                        self.screen.addstr(y, x, newchar, newcolor)
                        self.charlocations[self.cur_frame][y][x] = (
                            newchar, newcolor)
                    except curses.error:
                        pass
                self.times_modified += 1
        except IndexError:
            pass

    def reset_colors(self):
        curses.init_pair(1, curses.COLOR_BLACK, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)

    def change_color(self):
        self.color = curses.color_pair(ui.color_picker.get_color(self.screen))
        self.draw_frame()
        self.reset_colors()

    def clear(self, force=False):
        if force or ui.confirmation.confirm(self.screen, "Clear the screen?"):
            self.screen.clear()

            self.charlocations[self.cur_frame] = []
            for _ in range(curses.LINES):
                self.charlocations[self.cur_frame].append(
                    [(" ", self.color)] * curses.COLS
                )
        else:
            self.draw_frame()
        self.reset_colors()

    def _fill(self, y, x, original, replace):
        if (
            y > 0
            and x >= 0
            and y < len(self.charlocations[self.cur_frame])
            and x < len(self.charlocations[self.cur_frame][y])
        ):
            if (y, x) not in self.checked and self.in_selection(y, x):
                if self.charlocations[self.cur_frame][y][x] == original:
                    self.add_char(y, x)
                    self.checked.append((y, x))

                    self._fill(y + 1, x, original, replace)
                    self._fill(y - 1, x, original, replace)
                    self._fill(y, x + 1, original, replace)
                    self._fill(y, x - 1, original, replace)
                else:
                    self.checked.append((y, x))

    def draw_fill(self, y, x):
        self.checked = []
        original = self.charlocations[self.cur_frame][y][x]
        replace = (self.char, self.color)
        self._fill(y, x, original, replace)
        self.checked = []

    def draw_frame(self):
        for y, yval in enumerate(self.charlocations[self.cur_frame]):
            for x, xval in enumerate(yval):
                new_char, new_color = xval
                if new_char != " ":
                    try:
                        self.screen.addstr(y, x, new_char, new_color)
                    except curses.error:
                        pass
        self.draw_selection()

    def changeframe(self):
        self.screen.clear()
        self.history = [[]]
        self.recentlyadded = set()
        self.times_modified = 0
        self.remove_selection()
        self.draw_frame()

    def get_differences(self, otherframe=None):
        if otherframe is None:
            otherframe = self.cur_frame - 1
        diffs = []
        if otherframe == -1:
            for y, row in enumerate(self.charlocations[self.cur_frame]):
                for x, new_char in enumerate(row):
                    if new_char[0] != " ":
                        diffs.append(((y, x), new_char))
        else:
            for y, row in enumerate(self.charlocations[self.cur_frame]):
                for x, new_char in enumerate(row):
                    if new_char != self.charlocations[otherframe][y][x]:
                        diffs.append(((y, x), new_char))
        return diffs

    def next_frame(self):
        if self.cur_frame < self.frames - 1:
            self.cur_frame += 1
            self.changeframe()

    def last_frame(self):
        if self.cur_frame > 0:
            self.cur_frame -= 1
            self.changeframe()

    def play(self):
        print("\n" * 200)
        self.cur_frame = 0
        for frame in range(self.frames - 1):
            self.display_top()
            time.sleep(1 / self.fps)
            self.cur_frame += 1
            self.screen.clear()
            self.draw_frame()
            self.screen.refresh()

    def get_ansi_code_string(self, color, char, y, x):
        return f"\033[0;3{curses.pair_content(curses.pair_number(color))[0]}m\033[{y};{x}H{char}"

    def export(self):
        win = ui.window.make_adaptive_window(
            self.screen,
            title="Export file type",
            widgets=[
                (ui.widgets.ListItem, "Animation (python)", ""),
                (ui.widgets.ListItem, "Brush", ""),
            ],
            confirm=False,
        )
        response = ui.options.get_option(win)
        win.delete()
        if response == 1:
            export.export_brush(self, self.export_file)
        elif response == 0:
            export.export_animation(self)
        self.draw_frame()

    def save(self):
        win = ui.window.Window(self.screen)
        win.gen_window()
        win.gen_title("Save file")
        win.gen_widgets(
            [
                (
                    ui.widgets.TextInput,
                    "File location",
                    f"{self.save_path}/{self.project_name}",
                )
            ]
        )
        location, _ = win.get_contents()
        os.makedirs(os.path.dirname(location), exist_ok=True)
        with open(location, "wb") as f:
            pickle.dump(self.charlocations, f)
        win.delete()
        self.draw_frame()

    def load(self, location=""):
        if location == "":
            win = ui.window.Window(self.screen)
            win.gen_window()
            win.gen_title("Load file")
            win.gen_widgets(
                [(ui.widgets.TextInput, "File location", self.save_path)])
            location, _ = win.get_contents()
            win.delete()
        with open(location, "rb") as f:
            self.charlocations = pickle.load(f)
        self.draw_frame()

    def quit_drawing(self):
        if ui.confirmation.confirm(self.screen, "Quit the program?"):
            self.running = False
        self.draw_frame()

    def draw_selection(self):
        if self.init_coords is not None and self.final_coords is not None:
            for y in range(self.init_coords[0], self.final_coords[0]):
                # TODO: optimize
                for x in range(self.init_coords[1], self.final_coords[1] + 1):
                    char, color = self.charlocations[self.cur_frame][y][x]
                    self.screen.addstr(y, x, char, color | curses.A_REVERSE)

    def remove_selection(self):
        self.init_coords = None
        self.final_coords = None
        self.selecting = False
        self.screen.clear()
        self.draw_frame()

    def copy(self):
        if self.init_coords and self.final_coords:
            self.buffer = []
            for y in range(self.init_coords[0], self.final_coords[0]):
                xbuffer = []
                for x in range(self.init_coords[1], self.final_coords[1]):
                    xbuffer.append(self.charlocations[self.cur_frame][y][x])

                self.buffer.append(xbuffer)

    def paste(self):
        if self.buffer != []:
            key = self.screen.getch()
            ypos, xpos = 1, 0  # TODO: rewrite this whole part
            try:
                _, xpos, ypos, _, button = curses.getmouse()
                while (
                    button != curses.BUTTON1_PRESSED
                    and button != curses.BUTTON1_CLICKED
                    and key != 112
                ):
                    key = self.screen.getch()
                    try:
                        _, xpos, ypos, _, button = curses.getmouse()
                    except curses.error:
                        pass
            except curses.error:
                pass
            for y, yval in enumerate(self.buffer):
                for x, xval in enumerate(yval):
                    try:
                        self.history[self.times_modified].append(
                            (
                                ypos + y,
                                xpos + x,
                                self.charlocations[self.cur_frame][ypos + y][xpos + x][
                                    0
                                ],
                                xval[0],
                                self.charlocations[self.cur_frame][ypos + y][xpos + x][
                                    1
                                ],
                                yval[1],
                            )
                        )
                        self.charlocations[self.cur_frame][ypos +
                                                           y][xpos + x] = xval
                    except IndexError:
                        pass
            self.draw_frame()

    def select_all(self):  # TODO: FIX
        self.selecting = False
        self.init_coords = (1, 0)
        self.final_coords = (curses.LINES, curses.COLS - 2)
        self.draw_selection()

    def show_help(self):
        ui.help_menu.show_help(self.screen)
        self.draw_frame()

    def get_cur_brush(self):
        with open(f"{self.brush_dir}/{self.brush}") as f:
            brush_shapes = f.read().split("#SIZE\n")
            self.brush_size_max = len(brush_shapes)
            if self.brush_size >= len(brush_shapes) - 1:
                self.brush_shape = brush_shapes[-1]
            else:
                self.brush_shape = brush_shapes[self.brush_size]

    def decrease_size(self):
        if self.brush_size > 0:
            self.brush_size -= 1
            self.get_cur_brush()

    def increase_size(self):
        if self.brush_size < self.brush_size_max:
            self.brush_size += 1
            self.get_cur_brush()

    def select_brush(self):
        self.brush = ui.brush_picker.get_brush(self.screen, self.char)
        self.get_cur_brush()
        self.draw_frame()

    def settings(self):
        win = ui.window.Window(self.screen)
        win.gen_window()
        win.gen_title("animation settings")
        win.gen_widgets(
            [
                (ui.widgets.TextInput, "file name", "animation"),
                (ui.widgets.NumberInput, "total frames", "24"),
                (ui.widgets.NumberInput, "frames per second", "12"),
            ]
        )
        file_info = win.get_contents()
        self.project_name = file_info[0]
        self.frames = file_info[1]
        self.fps = file_info[2]
        win.delete()
        self.draw_frame()

    def get_keys(self):
        keybinds = {
            curses.KEY_MOUSE: self.react_to_mouse,  # On mouse movement
            100: self.toggle_draw,  # On 'd' pressed
            101: self.toggle_erase,  # On 'e' pressed
            114: self.toggle_modify,  # On 'r' pressed
            99: self.change_char,  # On 'c' pressed
            122: self.undo,  # On 'z' pressed
            90: self.redo,  # On 'Z' pressed
            115: self.change_color,  # On 's' pressed
            108: self.clear,  # On 'l' pressed
            102: self.toggle_fill,  # On 'f' pressed
            113: self.quit_drawing,  # On 'escape' pressed
            32: self.play,  # On space pressed
            111: self.export,  # On 'o' pressed
            83: self.save,  # On 's' pressed
            105: self.load,  # On 'i' pressed
            260: self.last_frame,  # On the left arrow pressed
            261: self.next_frame,  # On the right arrow pressed
            68: self.remove_selection,  # On 'D' pressed
            121: self.copy,  # On 'y' pressed
            112: self.paste,  # On 'p' pressed
            1: self.select_all,  # On Ctrl + 'a' pressed
            104: self.show_help,
            123: self.decrease_size,
            91: self.decrease_size,  # on '[' pressed
            125: self.increase_size,
            93: self.increase_size,  # on ']' pressed
            98: self.select_brush,
            107: self.settings,
            67: self.toggle_curve_mode,
        }

        if not self.playing:
            key = self.screen.getch()
            try:
                keybinds[key]()
            except KeyError:  # If the key pressed doesn't do anything ignore it
                pass

    def display_top(self):
        mode = "none"
        if self.erase:
            mode = "erase"
        elif self.draw:
            mode = "draw"
        elif self.fill:
            mode = "fill"
        if mode in ["erase", "draw"] and self.modify:
            mode += " (m)"

        # TODO: REWORK
        OPTIONS = [
            (f" {self.project_name}  ", curses.color_pair(29)),
            ("", curses.color_pair(30)),
            (f" {mode} ", curses.color_pair(25)),
            ("", curses.color_pair(27)),
            (f" frame: {self.cur_frame}", curses.color_pair(26)),
            ("", curses.color_pair(28)),
            (f"   {self.char}   ", curses.color_pair(25)),
        ]

        cur_width = 0
        for opt in OPTIONS:
            display, color = opt
            self.screen.addstr(0, cur_width, display, color)
            cur_width += len(display)


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
