from textual.app import ComposeResult
from textual.widgets import OptionList, Static, TabPane, TabbedContent
from ...api.forge_logs import ForgeLogsAPI, LambdaGroup
from .cloudwatch_single_log import CloudWatchSingleLog

LOGS_UPDATE_INTERVAL = 3


class CloudWatchLogs(Static):

    @property
    def logs_api(self) -> ForgeLogsAPI:
        return self.app.logs_api

    @property
    def parent_tab(self) -> TabPane:
        if isinstance(self.parent, TabPane):
            return self.parent

        raise ValueError("CloudWatchLogs must be a child of a TabPane")

    def reset_label(self):
        tabbed_content = self.app.query_one(
            "#cloud_watch_logs",
            expect_type=TabbedContent,
        )
        tab_pane = tabbed_content.get_tab(self.parent_tab)
        tab_pane.label = self.log_group.name

    def update_tab_label(self):
        if not self.new_logs:
            return self.reset_label()

        tabbed_content = self.app.query_one(
            "#cloud_watch_logs", expect_type=TabbedContent
        )
        tab_pane = tabbed_content.get_tab(self.parent_tab)
        tab_pane.label = f"{self.log_group.name} ({len(self.new_logs)})"

    @property
    def log_list(self) -> OptionList:
        return self.query_one(OptionList)

    def __init__(self, log_group: LambdaGroup):
        self.log_group = log_group
        self.logs = []
        self.new_logs = []
        super().__init__(id=log_group.name.replace("/", "-"))

    def on_mount(self):
        self.set_interval(LOGS_UPDATE_INTERVAL, self.update_logs)

    def update_logs(self):
        all_logs = list(self.logs_api.get_logs(self.log_group.name))
        self.new_logs = all_logs[len(self.logs) :]

        if not self.new_logs:
            return

        for log in self.new_logs:
            self.log_list.add_option(CloudWatchSingleLog(log))

        self.logs = all_logs
        self.update_tab_label()
        self.new_logs.clear()

    def compose(self) -> ComposeResult:
        yield OptionList()
