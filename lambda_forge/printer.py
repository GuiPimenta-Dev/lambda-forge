import itertools
import os
import sys
import threading
import time

import pyfiglet


class Printer:
    spinner = {"running": False, "legend": None, "thread": None}
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "light-gray": "\033[37m",
        "rose": "\033[38;2;244;94;172m",
        "black": "\033[38;2;0;0;0m",
    }

    def start_spinner(self, legend, color="white"):
        if self.spinner["running"]:
            self.stop_spinner()
        self.spinner["running"] = True
        self.spinner["legend"] = legend
        color = self.colors[color]
        spinner_thread = threading.Thread(target=self.spinner_task, args=(color,))
        spinner_thread.start()
        self.spinner["thread"] = spinner_thread

    def spinner_task(self, color="white"):
        spinner_symbols = itertools.cycle(["-", "\\", "|", "/"])
        while self.spinner["running"]:
            sys.stdout.write(f"\r{color}{next(spinner_symbols)}   {self.spinner['legend']}\033[0m")
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()
            time.sleep(0.1)

    def stop_spinner(self):
        if self.spinner["running"]:
            self.spinner["running"] = False
            self.spinner["thread"].join()
            sys.stdout.write("\r")
            sys.stdout.write(" " * (len(self.spinner["legend"]) + 4))
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

    def change_spinner_legend(self, legend):
        previous_legend_length = len(self.spinner["legend"]) + 4 if self.spinner["legend"] else 0
        sys.stdout.write("\r" + " " * previous_legend_length)
        sys.stdout.flush()
        self.spinner["legend"] = legend

    def print(self, message, color="white", pre_break_lines=None, post_break_lines=None):
        if pre_break_lines:
            print("\n" * pre_break_lines)

        color = self.colors[color]
        if color:
            print(color + message + "\033[0m")
        else:
            print(message)

        if post_break_lines:
            print("\n" * post_break_lines)

    def show_banner(self, text, color="rose"):
        print("\033[H\033[J", end="")
        os.system("clear")
        ascii_art = pyfiglet.figlet_format(text, width=200)
        self.print(ascii_art, color, 1)

    @staticmethod
    def br(lines=1):
        print("\n" * lines)
