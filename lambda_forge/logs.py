import itertools
import sys
import time
import threading
import pyfiglet


class Logger:
    spinner = {"running": False, "legend": None}
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "light-gray" : "\033[37m",
        "rose": "\033[38;2;244;94;172m", 
        "black": "\033[38;2;0;0;0m",      
    }

    def start_spinner(self):
        self.spinner["running"] = True
        spinner_thread = threading.Thread(target=self.spinner_task)
        spinner_thread.start()

    def spinner_task(self):
        spinner_symbols = itertools.cycle(["-", "\\", "|", "/"])
        while self.spinner["running"]:
            sys.stdout.write(f"\r{next(spinner_symbols)}   {self.spinner['legend']}")
            sys.stdout.flush()
            time.sleep(0.1)

    def stop_spinner(self):
        self.spinner["running"] = False
        sys.stdout.write("\r")  # Move cursor to the beginning of the line
        sys.stdout.write(" " * (len(self.spinner["legend"]) + 4))  # Overwrite spinner and legend with spaces
        sys.stdout.flush()

    def change_spinner_legend(self, legend):
        previous_legend_length = len(self.spinner["legend"]) + 4 if self.spinner["legend"] else 0
        sys.stdout.write("\r" + " " * previous_legend_length)
        sys.stdout.flush()
        self.spinner["legend"] = legend

    def log(self, message, color="white", pre_break_lines=None, post_break_lines=None):
        if pre_break_lines:
            print("\n" * pre_break_lines)

        color = self.colors[color]
        if color:
            print(color + message + "\033[0m")
        else:
            print(message)

        if post_break_lines:
            print("\n" * post_break_lines)

    def lambda_forge_gradient_figlet(text):
        figlet_text = pyfiglet.figlet_format(text, width=200)
        lines = figlet_text.split("\n")

        colors = [
            (244, 94, 172),  # Rose Bonbon
            (253, 205, 18),  # Mikado Yellow
            (22, 173, 175),  # Vivid Cerulean:
            (37, 171, 190),  # Light Sea Green
            (0, 0, 0),  # Black
        ]
        max_len = max(len(line) for line in lines)
        for line in lines:
            if line.strip():
                print_line = ""
                for i, char in enumerate(line):
                    num_colors = len(colors) - 1
                    color_index = int((i / max_len) * num_colors)
                    next_color_index = min(color_index + 1, num_colors)
                    factor = (i / max_len) * num_colors - color_index
                    color = interpolate_color(colors[color_index], colors[next_color_index], factor)
                    print_line += rgb_to_ansi(*color) + char
                print(print_line + "\x1b[0m")
            else:
                print()

            def rgb_to_ansi(r, g, b):
                return f"\x1b[38;2;{r};{g};{b}m"

            def interpolate_color(color1, color2, factor):
                r = int(color1[0] + (color2[0] - color1[0]) * factor)
                g = int(color1[1] + (color2[1] - color1[1]) * factor)
                b = int(color1[2] + (color2[2] - color1[2]) * factor)
                return (r, g, b)
