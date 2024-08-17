from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, TabPane, TabbedContent

from lambda_forge.live.tui.api.forge import ForgeAPI
from ..widgets import ForgeHeader, ServerTable, LogStream, Triggers

forge = ForgeAPI()


class IndexScreen(Screen):
    DEFAULT_CSS = """
    IndexScreen {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 4 1fr;
    }
    """

    BINDINGS = [
        Binding("s", "move_to_tab('server')", "Server"),
        Binding("l", "move_to_tab('logs')", "Server"),
        Binding("t", "move_to_tab('triggers')", "Server"),
    ]

    def action_move_to_tab(self, tab: str):
        self.tabbed_container.active = tab

    def compose(self) -> ComposeResult:
        yield ForgeHeader()
        with TabbedContent(initial="server") as t:
            self.tabbed_container = t

            with TabPane("Server", id="server"):
                yield ServerTable()

            with TabPane("Logs", id="logs"):
                yield LogStream(forge.get_log_file_path())

            with TabPane("Triggers", id="triggers"):
                yield Triggers()

        yield Footer()
