import ui.window


def export_brush(drawing, file: str):
    with open(file, "w") as f:
        for brush_size in drawing.charlocations:
            text = []
            start_height = 0
            start_width = len(brush_size[0])

            for y, row in enumerate(brush_size):
                row_text = []
                empty_row = True
                for i, (char, _) in enumerate(row):
                    if char != " " and i < start_width:
                        start_width = i
                        empty_row = False
                    row_text.append(char)
                if start_height + 1 == y and empty_row:
                    start_height = y
                text.append("".join(row_text))

            end_height_margin = 0
            end_width_margin = len(brush_size[0])
            for y, row in enumerate(reversed(brush_size)):
                empty_row = True
                for i, (char, _) in enumerate(reversed(row)):
                    if char != " ":
                        if i < end_width_margin:
                            end_width_margin = i
                            empty_row = False
                        break
                if end_height_margin + 1 == y and empty_row:
                    end_height_margin = y

            for line in text[start_height + 1 : -end_height_margin - 1]:
                f.write(line[start_width:-end_width_margin] + "\n")

            if text[start_height + 1 : -end_height_margin - 1] != []:
                f.write("#SIZE\n")


def export_animation(drawing):
    win = ui.window.Window(drawing.screen)
    win.gen_window()
    win.gen_title("Export file")
    win.gen_widgets(
        [
            (
                ui.widgets.TextInput,
                "File location",
                f"{drawing.export_file}",
            ),
            (
                ui.widgets.TextInput,
                "Loop (y/n)",
                "y",
            ),
        ]
    )
    drawing.export_file, loop, _ = win.get_contents()
    loop = loop.strip().lower().startswith("y")
    prefix = "\t" if loop else ""
    with open(drawing.export_file, "w") as f:
        f.write("import time\nprint('\\n' * 100)\n")
        drawing.cur_frame = 0

        # Handle the first frame outside of loop so that looping works
        f.write("# frame 0\n")
        f.write(f"time.sleep({1 / drawing.fps})\n")
        for coords, char_info in drawing.get_differences():
            y, x = coords
            new_char, new_char_color = char_info
            f.write(
                f"print('{drawing.get_ansi_code_string(new_char_color, new_char, y, x)}')\n"
            )
        drawing.cur_frame += 1

        if loop:
            f.write("while True:\n")
        for frame in range(1, drawing.frames):
            f.write(f"{prefix}# frame {frame}\n")
            f.write(f"{prefix}time.sleep({1 / drawing.fps})\n")
            for coords, char_info in drawing.get_differences():
                y, x = coords
                new_char, new_char_color = char_info
                f.write(
                    f"{prefix}print('{drawing.get_ansi_code_string(new_char_color, new_char, y, x)}')\n"
                )
            drawing.screen.clear()
            drawing.draw_frame()
            drawing.screen.refresh()
            drawing.cur_frame += 1

        if loop:
            f.write("# frame 0\n")
            f.write(f"\ttime.sleep({1 / drawing.fps})\n")
            drawing.cur_frame = 0
            for coords, char_info in drawing.get_differences(
                otherframe=drawing.frames - 1
            ):
                y, x = coords
                new_char, new_char_color = char_info
                f.write(
                    f"\tprint('{drawing.get_ansi_code_string(new_char_color, new_char, y, x)}')\n"
                )

    win.delete()
