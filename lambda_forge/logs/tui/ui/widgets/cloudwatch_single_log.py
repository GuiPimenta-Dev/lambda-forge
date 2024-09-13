from rich.table import Table
from textual.widgets.option_list import Option
from ...api.forge_logs import CloudWatchLog


class CloudWatchSingleLog(Option):

    def __init__(self, log: CloudWatchLog):
        super().__init__("")
        self.log = log
        self.tall = False
        self.refresh_prompt()

    def refresh_prompt(self):
        table = Table.grid(padding=(0, 0))
        table.add_column("timestamp", width=25)
        table.add_column("log_type", width=10)
        table.add_column("message")

        timestamp = self.log.timestamp.strftime("%Y-%m-%d (%H:%M)")

        table.add_row() # top padding
        table.add_row(timestamp, self.log.log_type.value, self.log.message)
        table.add_row() # bottom padding
        self.set_prompt(table)

    def toggle_display(self):
        self.tall = not self.tall
        self.refresh_prompt()
