from textual.app import App
from textual.binding import Binding
from .screens import IndexScreen


class ForgeTUI(App):
    SCREENS = {
        "index": IndexScreen(),
    }
    CSS_PATH = "styles.css"
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen("index")
