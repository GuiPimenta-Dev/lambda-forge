from textual import work
from textual.app import App
from .screens import Index
from ..api import ForgeLogsAPI


class ForgeLogsApp(App):
    CSS_PATH = "styles.css"
    SCREENS = {"index": Index()}

    def __init__(self, functions, log_file_path, stack, interval):
        super().__init__()
        self.logs_api = ForgeLogsAPI(functions, log_file_path, stack, interval)

    @work(thread=True)
    def watch_logs(self):
        self.logs_api.start_watcher()

    def on_mount(self) -> None:
        self.push_screen("index")
        self.watch_logs()
