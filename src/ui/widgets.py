import curses


class Widget:
    def __init__(self, screen, y, x, prompt, input_prompt=": ", fg=1):
        self.fg = fg
        self.screen = screen
        self.y = y
        self.x = x
        self.prompt = prompt
        self.input_prompt = input_prompt  # TODO: make name better
        self.answer = ""
        self.possible_inputs = ["up", "down", "escape"]

        self.active = False
        if fg == 0:
            curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)
        else:
            curses.init_pair(9 + fg, curses.pair_content(fg)
                             [0], curses.COLOR_WHITE)
        curses.init_pair(18, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.draw()

    def draw(self):
        color = 18 if self.active else 9 + self.fg
        self.cur_showing = self.prompt + self.input_prompt + self.answer
        self.screen.addstr(self.y, self.x, self.cur_showing,
                           curses.color_pair(color))

    def _input_response(self):
        char = self.screen.getkey()
        if char == "KEY_UP" or char == "k":
            self.active = False
            self.draw()
            return "up"
        elif char == "KEY_DOWN" or char == "j":
            self.active = False
            self.draw()
            return "down"
        elif char == "":
            return "escape"
        else:
            return char

    def get_input(self):
        self.active = True
        finished_input = False
        while not finished_input:
            self.draw()
            response = self._input_response()
            if response in self.possible_inputs:
                return response


class TextInput(Widget):
    def _input_response(self):
        response = super()._input_response()
        if response in self.possible_inputs:
            return response
        if response == "KEY_BACKSPACE":
            self.answer = self.answer[:-1]
            self.draw()
            self.screen.addstr(
                self.y,
                self.x + len(self.cur_showing),
                " ",
                curses.color_pair(9 + self.fg),
            )
        elif response == "\n":
            self.active = False
            self.draw()
            return "down"
        elif not response.startswith("KEY_"):
            self.answer += response


class NumberInput(TextInput):
    def __init__(self, screen, y, x, prompt):
        super().__init__(screen, y, x, prompt)
        curses.init_pair(19, curses.COLOR_WHITE, curses.COLOR_RED)

    def draw(self):
        color = 18 if self.active else 9 + self.fg
        try:
            self.answer = int(self.answer)
        except ValueError:
            color = 19
        self.cur_showing = self.prompt + self.input_prompt + str(self.answer)
        self.screen.addstr(self.y, self.x, self.cur_showing,
                           curses.color_pair(color))

    def _input_response(self):
        self.answer = str(self.answer)
        return super()._input_response()


class AcceptInput(Widget):
    def __init__(self, screen, y, x, prompt, fg=1):
        super().__init__(screen, y, x, prompt, input_prompt="", fg=fg)
        self.possible_inputs.append("finish")

    def _input_response(self):
        response = super()._input_response()
        if response in self.possible_inputs:
            return response
        if response == "\n":
            return "finish"
        return response


class ListItem(AcceptInput):
    def __init__(self, screen, y, x, prompt, fg=1):
        super().__init__(screen, y, x, prompt, fg=fg)
        self.possible_inputs = self.possible_inputs + [i for i in range(0, 10)]

    def _input_response(self):
        response = super()._input_response()
        if response.isnumeric():
            return int(response)
        else:
            return response


class PreviewListItem(AcceptInput):
    def __init__(self, screen, y, x, prompt, description, fg=1):
        self.description = description
        super().__init__(screen, y, x, prompt, fg=fg)
        self.possible_inputs = self.possible_inputs + ["KEY_LEFT", "KEY_RIGHT"]

    def draw(self):
        color = 18 if self.active else 9 + self.fg
        lines = self.prompt.split("\n")

        temp_start = False
        while len(lines) > 9:
            if temp_start:
                lines.pop(0)
            else:
                lines.pop()
            temp_start = not temp_start

        self.screen.addstr(self.y - 1,  self.x, self.description,
                           curses.color_pair(color))
        offset = 1
        if len(lines) < 9:
            offset += round((9 - len(lines)) / 2)

        max_len = len(max(lines, key=len))

        padding = ""
        if max_len < len(self.description):
            padding = " " * round((len(self.description) - max_len) / 2)
        for line_num, line in enumerate(lines):
            additional = (max_len - len(line)) * " "
            self.screen.addstr(self.y + offset + line_num, self.x, padding + line + additional + padding,
                               curses.color_pair(color))
