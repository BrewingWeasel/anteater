# USE export TERM=xterm-1003

import curses
import time


class Drawing:
    def __init__(self):
        # Initialize curses screen
        self.screen = curses.initscr()

        # Set up colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        # Set up other curses settings
        self.screen.keypad(1)
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.flushinp()
        curses.noecho()

        # TODO: Make these options that can be changed
        self.frames = 12
        self.export_file = "animation.py"

        self.cur_frame = 0
        self.playing = False
        self.running = True
        self.draw = True
        self.erase = False
        self.modify = False
        self.times_modified = 0
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

    def add_char(self, y, x, char_to_add="cur_char"):
        if char_to_add == "cur_char":
            char_to_add = self.char
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

    def unmodify(self):
        self.modify = False
        self.times_modified += 1
        self.history.append([])
        self.recentlyadded = []

    def react_to_mouse(self):
        _, x, y, _, button = curses.getmouse()
        if self.modify:
            if self.draw:
                self.add_char(y, x)
            if self.erase:
                self.add_char(y, x, char_to_add=" ")
        if button & curses.BUTTON1_PRESSED:
            self.modify = True
        if button & curses.BUTTON1_CLICKED:
            if not self.modify:
                if self.draw:
                    self.add_char(y, x)
                if self.erase:
                    self.add_char(y, x, char_to_add=" ")
            self.unmodify()
        elif button & curses.BUTTON1_RELEASED:
            self.unmodify()

    def toggle_draw(self):
        self.erase = False
        self.draw = True
        self.modify = False

    def toggle_erase(self):
        self.draw = False
        self.erase = True
        self.modify = False

    def toggle_modify(self):
        if self.modify:
            self.unmodify()
        else:
            self.draw = False
            self.erase = False

    def change_char(self):
        self.char = self.screen.getkey()

    def undo(self):
        if self.modify:
            self.unmodify()
        try:
            if len(self.history[self.times_modified - 1]):
                for i in self.history[self.times_modified - 1]:
                    y, x, oldchar, _newchar, oldcolor, _newcolor = i
                    self.screen.addstr(y, x, oldchar, oldcolor)
                    self.charlocations[self.cur_frame][y][x] = (oldchar, oldcolor)
                self.times_modified -= 1
        except IndexError:
            pass  # TODO: error system

    def redo(self):
        try:
            if len(self.history[self.times_modified]):
                for i in self.history[self.times_modified]:
                    y, x, _oldchar, newchar, _oldcolor, newcolor = i
                    self.screen.addstr(y, x, newchar, newcolor)
                    self.charlocations[self.cur_frame][y][x] = (newchar, newcolor)
                self.times_modified += 1
        except IndexError:
            pass  # TODO: error system

    def changecolor(self):
        colorchar = self.screen.getkey()
        try:
            self.color = curses.color_pair(int(colorchar))
        except ValueError:
            pass  # TODO: error system

    def clear(self):
        self.screen.clear()  # TODO: UI for confirming clear

        self.charlocations[self.cur_frame] = []
        for y in range(curses.LINES):
            self.charlocations[self.cur_frame].append([(" ", self.color)] * curses.COLS)

    def changeframe(self):
        self.screen.clear()
        self.history = [[]]
        self.recentlyadded = []
        self.times_modified = 0
        for y, yval in enumerate(self.charlocations[self.cur_frame]):
            for x, xval in enumerate(yval):
                new_char, new_color = xval
                if new_char != " ":
                    self.screen.addstr(y, x, new_char, new_color)

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
            time.sleep(0.3)
            self.cur_frame += 1
            for coords, char_info in self.get_differences():
                y, x = coords
                new_char, new_char_color = char_info
                print(self.get_ansi_code_string(new_char_color, new_char, y, x))

    def get_ansi_code_string(self, color, char, y, x):
        return f"\033[0;3{curses.pair_content(curses.pair_number(color))[0]}m\033[{y};{x}H{char}"

    def export(self):
        with open(self.export_file, "w") as f:
            f.write("import time\nprint('\\n' * 100)\n")
            self.cur_frame = 0
            for frame in range(self.frames - 1):
                f.write(f"# frame {frame}\n")
                f.write("time.sleep(0.2)\n")
                self.cur_frame += 1
                for coords, char_info in self.get_differences():
                    y, x = coords
                    new_char, new_char_color = char_info
                    f.write(
                        f"print('{self.get_ansi_code_string(new_char_color, new_char, y, x)}')\n"
                    )
                    self.screen.addstr(y, x, new_char, new_char_color)

    def quit(self):
        self.running = False

    def get_keys(self):

        keybinds = {
            curses.KEY_MOUSE: self.react_to_mouse,  # On mouse movement
            100: self.toggle_draw,  # On 'd' pressed
            101: self.toggle_erase,  # On 'e' pressed
            114: self.toggle_modify,  # On 'r' pressed
            99: self.change_char,  # On 'c' pressed
            122: self.undo,  # On 'z' pressed
            90: self.redo,  # On 'shift' and 'z' pressed
            115: self.changecolor,  # On 's' pressed
            108: self.clear,  # On 'l' pressed
            27: self.quit,  # On 'escape' pressed
            32: self.play,  # On space pressed
            111: self.export,  # On 'o' pressed
            260: self.last_frame,  # On the left arrow pressed
            261: self.next_frame,  # On the right arrow pressed
        }

        if not self.playing:
            key = self.screen.getch()
            try:
                keybinds[key]()
            except KeyError:  # If they key pressed doesn't do anything ignore it
                with open(
                    "keypressed.txt", "w"
                ) as f:  # add the key to logs for debugging purposes
                    f.write(str(key))
        else:
            pass

    def display_top(self):
        mode = "none"
        if self.erase:
            mode = "erase"
        elif self.draw:
            mode = "draw"

        if mode in ["erase", "draw"] and self.modify:
            mode += " (m)"
        self.screen.addstr(
            0,
            0,
            f"mode: {mode} char: {self.char} color: {self.color} frame: {self.cur_frame}",
        )


def main(stdscr):
    drawing = Drawing()

    while drawing.running:
        drawing.display_top()
        drawing.get_keys()


curses.wrapper(main)
