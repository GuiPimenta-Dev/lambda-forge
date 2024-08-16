from datetime import datetime
from rich import box
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text, TextType
from textual.widgets.option_list import Option
from ...api.forge_logs import CloudWatchLog


class CloudWatchSingleLog(Option):

    def __init__(self, log: CloudWatchLog):
        super().__init__("")
        self.log = log
        self.tall = False
        self.refresh_prompt()

    def refresh_prompt(self):
        table = Table.grid(padding=(0, 1))
        table.add_column("timestamp", width=25)
        table.add_column("log_type", width=10)
        table.add_column("message")

        timestamp = datetime.fromtimestamp(self.log.timestamp).strftime(
            "%Y-%m-%d (%H:%M)"
        )
        table.add_row(timestamp, self.log.log_type.value, self.log.message)
        self._set_prompt(table)

    def _set_prompt(self, prompt: RenderableType):
        self.set_prompt(prompt)
        #
        # self.set_prompt(
        #     Panel(
        #         prompt,
        #         box=box.ROUNDED,
        #     )
        # )

    def toggle_display(self):
        self.tall = not self.tall
        self.refresh_prompt()
