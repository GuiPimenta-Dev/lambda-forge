from rich.align import Align
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class RunHistoryItem(Option):
    def __init__(self, history):
        super().__init__("")
        self.history = history
        self.refresh_option()

    def refresh_option(self):

        formatted = Text()
        for key, value in list(self.history.items())[:3]:
            formatted += Text.assemble(
                Text(),
                Text(f"{key}: "),
                Text(str(value)),
                Text("\n"),
            )

        formatted.rstrip()

        repeat_icon = ""
        repeat_text = Align(
            Text(repeat_icon),
            vertical="middle",
            align="center",
        )

        t = Table(expand=True, show_header=False)
        t.add_column("data", ratio=1)
        t.add_column("repeat", width=3)
        t.add_row(formatted, repeat_text)

        self.set_prompt(t)

    def __str__(self) -> str:
        return str(self.history)


class ResultWindow(Widget):
    DEFAULT_CSS = """
    ResultWindow > OptionList {
        height: 100%;
    }
    """

    @property
    def history_list(self) -> OptionList:
        return self.query_one(OptionList)

    def compose(self) -> ComposeResult:
        yield OptionList()

    def add_history(self, history):
        self.history_list.add_option(RunHistoryItem(history))
