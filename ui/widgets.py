import curses


class Widget:
    def __init__(self, screen, y, x, prompt, input_prompt=": "):
        self.screen = screen
        self.y = y
        self.x = x
        self.prompt = prompt
        self.input_prompt = input_prompt  # TODO: make name better
        self.answer = ""

        self.active = False

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
        self.draw()

    def draw(self):
        color = 2 if self.active else 1
        self.cur_showing = self.prompt + self.input_prompt + self.answer
        self.screen.addstr(self.y, self.x, self.cur_showing, curses.color_pair(color))

    def _input_response(self):
        char = self.screen.getkey()  # TODO: make enter work
        if char == "KEY_UP":
            self.active = False
            finished_input = True
            self.draw()
            return "up"
        elif char == "KEY_DOWN":
            self.active = False
            finished_input = True
            self.draw()
            return "down"
        else:
            return char

    def get_input(self):
        self.active = True
        finished_input = False
        while not finished_input:
            self.draw()
            response = self._input_response()
            if response in ["up", "down", "finish"]:
                return response


class TextInput(Widget):
    def _input_response(self):
        response = super()._input_response()
        if response in ["up", "down"]:
            return response
        if response == "KEY_BACKSPACE":
            self.answer = self.answer[:-1]
            self.draw()
            self.screen.addstr(
                self.y, self.x + len(self.cur_showing), " ", curses.color_pair(1)
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
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)

    def draw(self):
        color = 2 if self.active else 1
        try:
            self.answer = int(self.answer)
        except ValueError:
            color = 3
        self.cur_showing = self.prompt + self.input_prompt + str(self.answer)
        self.screen.addstr(self.y, self.x, self.cur_showing, curses.color_pair(color))

    def _input_response(self):
        self.answer = str(self.answer)
        return super()._input_response()


class AcceptInput(Widget):
    def __init__(self, screen, y, x, prompt):
        super().__init__(screen, y, x, prompt, input_prompt="")

    def _input_response(self):
        response = super()._input_response()
        if response in ["up", "down"]:
            return response
        if response == "\n":
            return "finish"
        return response


class ListItem(AcceptInput):
    def _input_response(self):
        response = super()._input_response()
        if response.isnumeric():
            return int(response)
        else:
            return response