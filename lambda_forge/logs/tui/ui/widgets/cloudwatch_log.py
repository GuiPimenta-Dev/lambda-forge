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

    @property
    def tabbed_content(self) -> TabbedContent:
        return self.app.query_one("#cloud_watch_logs", expect_type=TabbedContent)

    def reset_logs(self):
        self.logs.extend(self.new_logs)
        self.new_logs.clear()
        self.update_tab_label()

    def update_tab_label(self):
        tab_pane = self.tabbed_content.get_tab(self.parent_tab)
        label = self.log_group.group

        if self.new_logs:
            label += f" ({len(self.new_logs)})"

        tab_pane.label = label

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

        for log in all_logs[len(self.log_list._options) :]:
            self.log_list.add_option(CloudWatchSingleLog(log))

        self.update_tab_label()

        if self.parent_tab.id == self.tabbed_content.active:
            self.reset_logs()

    def compose(self) -> ComposeResult:
        yield OptionList()
