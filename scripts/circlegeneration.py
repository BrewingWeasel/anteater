import math

INITIAL_FILLED = """*
#SIZE
 ***
*****
 ***
"""

INITIAL_UNFILLED = """*
#SIZE
 ***
*   *
 ***
"""


def get_circle(radius, count=200):
    conts = []
    for y in range(radius * 2 + 1):
        conts.append([" "] * (radius * 4 + 1))
    for angle in range(1, count):
        angle = angle * (360 / count)
        x = radius * math.cos(angle) * 2
        y = radius * math.sin(angle)
        conts[radius + round(y)][radius * 2 + round(x)] = "*"
    return conts


def fill_inside(conts):
    for y_index, line in enumerate(conts):
        if y_index == 0 or y_index == len(conts) - 1:
            continue
        begun = False
        lastAsterisk = True
        for x_index, x in enumerate(line):
            if x == " " and begun:
                conts[y_index][x_index] = "*"
            if x == "*":
                if begun:
                    if not lastAsterisk:
                        break
                begun = True
                lastAsterisk = True
            else:
                lastAsterisk = False
    return conts


def gen_file(file_name="brushes/default", fill=True):
    with open(file_name, "w") as f:
        if fill:
            f.write(INITIAL_FILLED)
        else:
            f.write(INITIAL_UNFILLED)
        for radius in range(2, 15):
            f.write("#SIZE\n")
            conts = get_circle(radius)
            if fill:
                conts = fill_inside(conts)
            for y in conts:
                f.write("".join(y) + "\n")


if __name__ == "__main__":
    gen_file()
    gen_file(file_name="brushes/outline", fill=False)
