# USE export TERM=xterm-1003
import os
import sys
import curses
import time
import pickle
import ui.window
import ui.color_picker
import ui.confirmation
import ui.start_window
import ui.help_menu


class Drawing:
    def __init__(self, frames=12, fps=12, project_name="animation"):
        # Initialize curses screen
        self.screen = curses.initscr()

        # Set up colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        self.screen.keypad(1)
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.flushinp()
        curses.noecho()

        usrdir = os.path.expanduser("~")
        self.save_path = os.path.join(usrdir, ".local", "share", "anteater")

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

        self.char = "a"
        self.color = curses.COLOR_WHITE
        self.mode = "none"

        self.charlocations = []
        for frame in range(self.frames):
            framelocations = []
            for y in range(curses.LINES):
                framelocations.append([(" ", self.color)] * curses.COLS)
            self.charlocations.append(framelocations)

        self.history = [[]]
        self.recentlyadded = []

        self.screen.clear()

    def in_selection(self, y, x):
        if self.final_coords is None:
            return True
        elif (
            self.final_coords[0] >= y >= self.init_coords[0]
            and self.final_coords[1] >= x >= self.init_coords[1]
        ):
            return True
        return False

    def add_char(self, y, x, char_to_add="cur_char"):
        if char_to_add == "cur_char":
            char_to_add = self.char
        try:
            if y > 0 and self.in_selection(y, x):
                self.screen.addstr(y, x, char_to_add, self.color)

                oldchar = self.charlocations[self.cur_frame][y][x][0]
                oldcolor = self.charlocations[self.cur_frame][y][x][1]

                if (y, x) in self.recentlyadded:
                    index = self.recentlyadded.index((y, x))

                    self.recentlyadded.pop(index)
                    oldinfo = self.history[self.times_modified].pop(index)
                    oldchar = oldinfo[2]
                    oldcolor = oldinfo[4]

                self.history[self.times_modified].append(
                    (y, x, oldchar, char_to_add, oldcolor, self.color)
                )
                self.recentlyadded.append((y, x))
                self.charlocations[self.cur_frame][y][x] = (char_to_add, self.color)
        except curses.error:
            pass  # TODO: Error system

    def unmodify(self):
        self.modify = False
        self.times_modified += 1
        self.history.append([])
        self.recentlyadded = []
        self.draw_selection()

    def react_to_mouse(self):
        _, x, y, _, button = curses.getmouse()
        if self.modify:
            if self.draw:
                self.add_char(y, x)
            if self.erase:
                self.add_char(y, x, char_to_add=" ")
        if button & curses.BUTTON1_PRESSED:
            self.modify = True
            if self.fill:
                self.draw_fill(y, x)
        elif button & curses.BUTTON1_CLICKED:
            if not self.modify:
                if self.draw:
                    self.add_char(y, x)
                if self.erase:
                    self.add_char(y, x, char_to_add=" ")
            self.unmodify()
        elif button & curses.BUTTON1_RELEASED:
            self.unmodify()
        elif button & curses.BUTTON3_PRESSED:
            if not self.selecting:
                self.remove_selection()
                print("lol")
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

    def toggle_draw(self):
        self.erase = False
        self.draw = True
        self.modify = False
        self.fill = False

    def toggle_erase(self):
        self.draw = False
        self.erase = True
        self.modify = False
        self.fill = False

    def toggle_fill(self):
        self.draw = False
        self.erase = False
        self.modify = False
        self.fill = True

    def toggle_modify(self):
        if self.modify:
            self.unmodify()
        else:
            self.draw = False
            self.erase = False

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
                        self.charlocations[self.cur_frame][y][x] = (oldchar, oldcolor)
                    except curses.error:
                        pass
                self.times_modified -= 1
        except IndexError:
            # TODO: error system
            pass

    def redo(self):
        try:
            if len(self.history[self.times_modified]):
                for i in self.history[self.times_modified]:
                    y, x, _oldchar, newchar, _oldcolor, newcolor = i
                    try:
                        self.screen.addstr(y, x, newchar, newcolor)
                        self.charlocations[self.cur_frame][y][x] = (newchar, newcolor)
                    except curses.error:
                        pass
                self.times_modified += 1
        except IndexError:
            pass  # TODO: error system

    def reset_colors(self):
        curses.init_pair(1, curses.COLOR_BLACK, -1)
        curses.init_pair(2, curses.COLOR_RED, -1)

    def change_color(self):
        self.color = curses.color_pair(ui.color_picker.get_color(self.screen))
        self.draw_frame()
        self.reset_colors()

    def clear(self, force=False):
        if ui.confirmation.confirm(self.screen, "Clear the screen?"):
            self.screen.clear()

            self.charlocations[self.cur_frame] = []
            for y in range(curses.LINES):
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
                    self.charlocations[self.cur_frame][y][x] = replace
                    self.history[self.times_modified].append(
                        (y, x, original[0], replace[0], original[1], replace[1])
                    )
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
        self.draw_frame()
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
        self.recentlyadded = []
        self.times_modified = 0
        self.remove_selection()
        self.draw_frame()

    def get_differences(self, otherframe=None):
        if otherframe is None:
            otherframe = self.cur_frame - 1
        diffs = []
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
        # Print each frame
        for frame in range(self.frames - 1):
            self.display_top()
            time.sleep(1 / self.fps)
            self.cur_frame += 1
            for coords, char_info in self.get_differences():
                y, x = coords
                new_char, new_char_color = char_info
                print(self.get_ansi_code_string(new_char_color, new_char, y, x))

    def get_ansi_code_string(self, color, char, y, x):
        return f"\033[0;3{curses.pair_content(curses.pair_number(color))[0]}m\033[{y};{x}H{char}"

    def export(self):
        win = ui.window.Window(self.screen)
        win.gen_window()
        win.gen_title("Save file")
        win.gen_widgets(
            [
                (
                    ui.widgets.TextInput,
                    "File location",
                    f"{self.export_file}",
                )
            ]
        )
        self.export_file, _ = win.get_contents()
        with open(self.export_file, "w") as f:
            f.write("import time\nprint('\\n' * 100)\n")
            self.cur_frame = 0
            for frame in range(self.frames - 1):
                f.write(f"# frame {frame}\n")
                f.write(f"time.sleep({1 / self.fps})\n")
                self.cur_frame += 1
                for coords, char_info in self.get_differences():
                    y, x = coords
                    new_char, new_char_color = char_info
                    f.write(
                        f"print('{self.get_ansi_code_string(new_char_color, new_char, y, x)}')\n"
                    )
                    self.screen.addstr(y, x, new_char, new_char_color)
        win.delete()

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
            win.gen_widgets([(ui.widgets.TextInput, "File location", self.save_path)])
            location, _ = win.get_contents()
            win.delete()
        with open(location, "rb") as f:
            self.charlocations = pickle.load(f)
        self.draw_frame()

    def quit_drawing(self):
        self.running = False

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
                        self.charlocations[self.cur_frame][ypos + y][xpos + x] = xval
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
            # 27: self.quit_drawing,  # On 'escape' pressed
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
        }

        if not self.playing:
            key = self.screen.getch()
            try:
                keybinds[key]()
            except KeyError:  # If they key pressed doesn't do anything ignore it
                print(key)
        else:
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
        self.screen.addstr(
            0,
            0,
            f"mode: {mode} char: {self.char} color: {self.color} frame: {self.cur_frame} modified: {self.times_modified}",
        )


def main(stdscr):
    sys.setrecursionlimit(10000)  # Used for fill

    project = ui.start_window.start_window(stdscr)

    if project == "new":
        win = ui.window.Window(stdscr)

        win.gen_window()
        win.gen_title("new animation")
        win.gen_widgets(
            [
                (ui.widgets.TextInput, "file name", "animation"),
                (ui.widgets.NumberInput, "total frames", "24"),
                (ui.widgets.NumberInput, "frames per second", "12"),
            ]
        )
        file_info = win.get_contents()

        drawing = Drawing(
            project_name=file_info[0], frames=int(file_info[1]), fps=int(file_info[2])
        )

    else:
        drawing = Drawing()
        drawing.load(os.path.join(drawing.save_path, project))

    drawing.show_help()
    
    while drawing.running:
        drawing.display_top()
        drawing.get_keys()


curses.wrapper(main)
