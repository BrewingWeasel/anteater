# USE export TERM=xterm-1003

import curses

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

        self.running = True
        self.draw = True
        self.erase = False
        self.modify = False
        self.times_modified = 0
        self.char = "a"
        self.color = curses.COLOR_WHITE
        self.mode = "none"
        self.charlocations = []
        for y in range(curses.LINES):
            self.charlocations.append([(" ", self.color)] * curses.COLS)

        self.history = [[]]
        self.recentlyadded = []

        self.screen.clear()

    def add_char(self, y, x, char_to_add="cur_char"):
        if(char_to_add == "cur_char"):
            char_to_add = self.char
        self.screen.addstr(y, x, char_to_add, self.color)
        
        oldchar = self.charlocations[y][x][0]
        oldcolor = self.charlocations[y][x][1]
        
        if((y, x) in self.recentlyadded):
            index = self.recentlyadded.index((y, x))

            self.recentlyadded.pop(index)
            oldinfo = self.history[self.times_modified].pop(index)
            oldchar = oldinfo[2]
            oldcolor = oldinfo[4]
        
        self.history[self.times_modified].append(
            (y, x, oldchar, char_to_add, oldcolor, self.color)
        )
        self.recentlyadded.append((y, x))
        self.charlocations[y][x] = (char_to_add, self.color)
    
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
        if(self.modify):
            self.unmodify()
        try:
            if(len(self.history[self.times_modified - 1])):
                for i in self.history[self.times_modified - 1]:
                    y, x, oldchar, _newchar, oldcolor, _newcolor = i
                    self.screen.addstr(y, x, oldchar, oldcolor)
                    self.charlocations[y][x] = (oldchar, oldcolor)
                self.times_modified -= 1
        except IndexError:
            pass  # TODO: error system

    def redo(self):
        try:
            if(len(self.history[self.times_modified])):
                for i in self.history[self.times_modified]:
                    y, x, _oldchar, newchar, _oldcolor, newcolor = i
                    self.screen.addstr(y, x, newchar, newcolor)
                    self.charlocations[y][x] = (newchar, newcolor)
                self.times_modified += 1
        except IndexError:
            pass # TODO: error system

    def changecolor(self):
        colorchar = self.screen.getkey()
        try:
            self.color = curses.color_pair(int(colorchar))
        except ValueError:
            pass  # TODO: error system

    def quit(self):
        with open("cool.txt", "w") as f:
            f.write(
                str(self.charlocations)
                .replace("[", "")
                .replace("]", "")
                .replace(", ", "")
                .replace("0", " ")
                .replace("'", "")
            )
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
            27: self.quit,  # On 'escape' pressed
        }

        key = self.screen.getch()
        try:
            keybinds[key]()
        except KeyError:  # If they key pressed doesn't do anything ignore it
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
            0, 0, f"mode: {mode} char: {self.char} timesmodified: {self.times_modified} total: {len(self.history)} last: {len(self.history[self.times_modified])}"
        )


def main(stdscr):
    drawing = Drawing()

    while drawing.running:
        drawing.display_top()
        drawing.get_keys()


curses.wrapper(main)
