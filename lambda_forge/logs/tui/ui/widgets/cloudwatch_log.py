from rich.console import RenderableType
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Static, TabPane, TabbedContent
from ...api.forge_logs import ForgeLogsAPI
from .cloudwatch_single_log import CloudWatchSingleLog

LOGS_UPDATE_INTERVAL = 3


class CloudWatchLogs(Static):
    DEFAULT_CSS = """
    CloudWatchLogs {
        height: 1fr;
        content-align: center middle;
    }
    """

    BINDINGS = [ Binding("c", "clear_logs") ]

    COMPONENT_CLASSES = {
        "log-error",
        "log-warning",
        "log-info",
        "log-debug",
        "timestamp",
    }

    @property
    def logs_api(self) -> ForgeLogsAPI:
        return self.app.logs_api

    def action_clear_logs(self):
        self.logs_api.clear_logs()
        self.log_list.clear()
        self.logs = []
        self.new_logs = []
        self.update_tab_label()

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
        label = Text(self.lambda_name)

        post_attach = Text()

        if self.new_logs:
            errors = len([log for log in self.new_logs if log.is_error])
            non_errors = len(self.new_logs) - errors

            if errors:
                style = self.get_component_rich_style("log-error")
                post_attach += Text(f"⚠ {errors} ", style=style)

            if non_errors:
                style = self.get_component_rich_style("log-info")
                post_attach += Text(f"● {non_errors} ", style=style)

            if post_attach:
                post_attach = Text(" ") + post_attach

            label += Text(" [ ") + post_attach + Text(" ] ")

        tab_pane.label = label

    @property
    def log_list(self) -> DataTable[CloudWatchSingleLog]:
        return self.query_one(DataTable)

    def __init__(self, lambda_name: str):
        self.lambda_name = lambda_name
        self.logs = []
        self.new_logs = []
        super().__init__(id=lambda_name)

    def on_mount(self):
        self.set_interval(LOGS_UPDATE_INTERVAL, self.update_logs)
        self.log_list.display = False

    def update_logs(self):
        # self.log_list.clear()

        all_logs = list(self.logs_api.get_logs(self.lambda_name))
        self.new_logs = all_logs[len(self.logs) :]

        if not self.new_logs:
            return

        for log in all_logs[len(self.log_list.rows) :]:
            self.log_list.display = True
            self.log_list.add_row(CloudWatchSingleLog(log), height = None)

        self.update_tab_label()

        if self.parent_tab.id == self.tabbed_content.active:
            self.reset_logs()

    def compose(self) -> ComposeResult:
        dt = DataTable()
        dt.add_column('Logs')
        dt.show_header = False
        dt.zebra_stripes = True
        yield dt

    def render(self) -> RenderableType:
        return "No logs available yet for this lambda function."

    def on_show(self):
        self.log_list.focus()
