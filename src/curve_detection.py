class Curve:
    def __init__(self):
        self.locs = [(0, 0), (0, 0)]

    def get_char(self):  # TODO CLEAN UP AND IMPROVE NAMES ETC
        y, x = self.locs[-1]
        try:
            last_y, last_x = self.locs[-2]
        except IndexError:
            return "-"

        previous_y, previous_x = self.locs[-3]

        if last_y == y:
            if previous_y == y:
                return "-"
        if last_x == x:
            if self.locs[-3][1] == x:
                return "|"

        if (previous_x > x and previous_y < y) or (previous_x < x and previous_y > y):
            return "/"
        if (previous_x < x and previous_y < y) or (previous_x > x and previous_y > y):
            return "\\"
        return "/"

    def __call__(self, pos):
        self.locs.append(pos)
