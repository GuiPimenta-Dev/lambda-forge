from textual.app import ComposeResult, on
from textual.screen import Screen
from textual.widgets import TabbedContent, TabPane
from lambda_forge.logs.tui.api.forge_logs import ForgeLogsAPI
from lambda_forge.logs.tui.ui.widgets.cloudwatch_log import CloudWatchLogs


class Index(Screen):

    @property
    def logs_api(self) -> ForgeLogsAPI:
        return self.app.logs_api

    def compose(self) -> ComposeResult:
        with TabbedContent(id="cloud_watch_logs"):

            for log_group in self.logs_api.get_lambdas():
                with TabPane(log_group.group):
                    yield CloudWatchLogs(log_group)

    @on(TabbedContent.TabActivated)
    def _tab_activated(self, event: TabbedContent.TabActivated):
        event.pane.query_one(CloudWatchLogs).reset_logs()
