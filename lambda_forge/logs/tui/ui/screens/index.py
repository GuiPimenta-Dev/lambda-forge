from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, TabbedContent, TabPane


class Index(Screen):
    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("CloudWatch Logs"):
                yield Static()
