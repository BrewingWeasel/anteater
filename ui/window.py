import curses
import ui.widgets as widgets


class Window:
    def __init__(self, screen, margins=(4, 4)):
        self.screen = screen
        self.xmargin, self.ymargin = margins
        self.widgets = []
        self.cur_widget = 0
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def gen_window(self):
        for y in range(self.ymargin, curses.LINES - self.ymargin):
            self.screen.addstr(
                y,
                self.xmargin,
                " " * (curses.COLS - self.xmargin * 2),
                curses.color_pair(1),
            )

    def gen_title(self, title):
        xpos = round(
            curses.COLS / 2 - len(title) / 2
        )  # TODO: maybe find a better soloution
        self.screen.addstr(
            self.ymargin + 1, xpos, title, curses.color_pair(1) | curses.A_UNDERLINE
        )

    def gen_widgets(self, widget_list, confirm=True):
        for i, widget in enumerate(widget_list):
            widget_type, name, answer = widget
            self.widgets.append(
                widget_type(self.screen, self.ymargin + 3 + i, self.xmargin + 5, name)
            )
            self.widgets[i].answer = answer  # TODO: make this an input
            self.widgets[i].draw()
        if confirm:
            self.widgets.append(
                widgets.AcceptInput(
                    self.screen,
                    self.ymargin + 3 + len(self.widgets) + 3,
                    self.xmargin + 5,
                    "Enter",
                )
            )

    def get_contents(self):
        finished = False
        while not finished:
            response = self.widgets[self.cur_widget].get_input()
            if response == "up":
                self.cur_widget -= 1 if self.cur_widget > 0 else 0
            if response == "down":
                if self.cur_widget < len(self.widgets) - 1:
                    self.cur_widget += 1
            if response == "finish":
                finished = True
                return [i.answer for i in self.widgets]

    def delete(self):
        for y in range(self.ymargin, curses.LINES - self.ymargin):
            self.screen.addstr(y, self.xmargin, " " * (curses.COLS - self.xmargin * 2))