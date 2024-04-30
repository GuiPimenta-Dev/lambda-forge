import itertools
import sys
import time
import threading


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
