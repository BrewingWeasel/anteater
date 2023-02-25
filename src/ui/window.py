import curses
import ui.widgets as widgets


class Window:
    def __init__(self, screen, margins=(4, 4), size=(3, 20)):
        self.screen = screen

        self.xmargin, self.ymargin = margins
        if size != (3, 20):  # TODO make everything use size
            self.xmargin = round((curses.COLS - size[0]) / 2)
            self.ymargin = round((curses.LINES - size[1]) / 2)
        self.widgets = []
        self.cur_widget = 0
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def gen_window(self):
        for y in range(self.ymargin, curses.LINES - self.ymargin):
            self.screen.addstr(
                y,
                self.xmargin,
                " " * (curses.COLS - self.xmargin * 2),
                curses.color_pair(9),
            )

    def gen_title(self, title):
        xpos = round(curses.COLS / 2 - len(title) / 2)
        self.screen.addstr(
            self.ymargin, xpos, title, curses.color_pair(9) | curses.A_UNDERLINE
        )

    def gen_text(self, text, ypos="center", xpos="center", style=curses.A_NORMAL):
        if ypos == "center":
            ypos = round(curses.LINES / 2)
        else:
            ypos = self.ymargin + ypos

        if xpos == "center":
            xpos = round(curses.COLS / 2 - len(text) / 2)
        else:
            xpos = self.xmargin + xpos

        self.screen.addstr(ypos, xpos, text, curses.color_pair(9) | style)

    def gen_widgets(self, widget_list, confirm=True, offset=2):
        for i, widget in enumerate(widget_list):
            color = None
            if len(widget) > 3:
                widget_type, name, answer, color = widget
            else:
                widget_type, name, answer = widget

            # TODO Maybe clean up
            if color is None:
                self.widgets.append(
                    widget_type(
                        self.screen,
                        self.ymargin + offset + i,
                        self.xmargin + 5,
                        name,
                    )
                )
            else:
                self.widgets.append(
                    widget_type(
                        self.screen,
                        self.ymargin + offset + i,
                        self.xmargin + 5,
                        name,
                        fg=color,
                    )
                )
            self.widgets[-1].answer = answer
            self.widgets[-1].draw()
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
        while True:
            response = self.widgets[self.cur_widget].get_input()
            if response == "up":
                self.cur_widget -= 1 if self.cur_widget > 0 else 0
            if response == "down":
                if self.cur_widget < len(self.widgets) - 1:
                    self.cur_widget += 1
            if response == "finish":
                return [i.answer for i in self.widgets]
            if response == "cancel":
                return

    def delete(self):
        for y in range(self.ymargin, curses.LINES - self.ymargin):
            self.screen.addstr(y, self.xmargin, " " * (curses.COLS - self.xmargin * 2))


def make_adaptive_window(
    screen,
    widgets=[],
    text=[],
    title="",
    widgxmargin=2,
    requiredx=0,
    confirm=True,
    widgymargin=1,
):
    minx = len(title)
    for i in widgets:
        minx = max(len(i[1]), minx)
    for i in text:
        minx = max(len(i[1]), minx)

    miny = 1 if title == "" else 2
    miny += len(widgets) + len(text)
    win = Window(
        screen, size=(minx + widgxmargin * 2 + requiredx + 2, miny + widgymargin)
    )
    win.gen_window()
    win.gen_title(title)
    win.gen_widgets(widgets, confirm=confirm)
    return win
