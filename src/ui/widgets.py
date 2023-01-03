import curses


class Widget:
    def __init__(self, screen, y, x, prompt, input_prompt=": ", fg=2):
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
            curses.init_pair(9 + fg, curses.pair_content(fg)[0], curses.COLOR_WHITE)
        curses.init_pair(18, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.draw()

    def draw(self):
        color = 18 if self.active else 9+self.fg
        self.cur_showing = self.prompt + self.input_prompt + self.answer
        self.screen.addstr(self.y, self.x, self.cur_showing, curses.color_pair(color))

    def _input_response(self):
        char = self.screen.getkey()  # TODO: make enter work
        if char == "KEY_UP" or char == "k":
            self.active = False
            finished_input = True
            self.draw()
            return "up"
        elif char == "KEY_DOWN" or char == "j":
            self.active = False
            finished_input = True
            self.draw()
            return "down"
        elif char == "^[":
            # TODO: make this actually work
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
                self.y, self.x + len(self.cur_showing), " ", curses.color_pair(9+self.fg)
            )
        elif response == "\n":
            self.active = False
            finished_input = True
            self.draw()
            return "down"
        elif not response.startswith("KEY_"):
            self.answer += response


class NumberInput(TextInput):
    def __init__(self, screen, y, x, prompt):
        super().__init__(screen, y, x, prompt)
        curses.init_pair(19, curses.COLOR_WHITE, curses.COLOR_RED)

    def draw(self):
        color = 18 if self.active else 9+self.fg
        try:
            self.answer = int(self.answer)
        except ValueError:
            color = 19
        self.cur_showing = self.prompt + self.input_prompt + str(self.answer)
        self.screen.addstr(self.y, self.x, self.cur_showing, curses.color_pair(color))

    def _input_response(self):
        self.answer = str(self.answer)
        return super()._input_response()


class AcceptInput(Widget):
    def __init__(self, screen, y, x, prompt, fg=2):
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
    def __init__(self, screen, y, x, prompt, fg=2):
        super().__init__(screen, y, x, prompt, fg=fg)
        self.possible_inputs = self.possible_inputs + [i for i in range(0, 10)]

    def _input_response(self):
        response = super()._input_response()
        if response.isnumeric():
            return int(response)
        else:
            return response
