from textual.app import ComposeResult, on
from textual.screen import Screen
from textual.widgets import TabbedContent, TabPane
from lambda_forge.logs.tui.api.forge_logs import ForgeLogsAPI
from lambda_forge.logs.tui.ui.widgets.cloudwatch_log import CloudWatchLogs
from ..widgets import ForgeLogsHeader


class Index(Screen):
    DEFAULT_CSS = """
    Index {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 4 1fr;
    }
    """

    @property
    def logs_api(self) -> ForgeLogsAPI:
        return self.app.logs_api

    def compose(self) -> ComposeResult:
        yield ForgeLogsHeader()
        with TabbedContent(id="cloud_watch_logs"):
            for name in self.logs_api.get_lambdas():
                with TabPane(name):
                    yield CloudWatchLogs(name)

    @on(TabbedContent.TabActivated)
    def _tab_activated(self, event: TabbedContent.TabActivated):
        event.pane.query_one(CloudWatchLogs).reset_logs()
