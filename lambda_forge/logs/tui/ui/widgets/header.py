from rich.text import Text
from textual.widget import Widget


class ForgeLogsHeader(Widget):
    DEFAULT_CSS = """
    ForgeLogsHeader {
        padding: 1 4;
    }
    """

    COMPONENT_CLASSES = {"title", "subtitle"}

    def __init__(
        self,
        title: str = "λ Lambda Forge Logs",
        subtitle: str = "Simplify AWS Lambda Cloudwatch Logs",
    ):
        super().__init__()
        self.title = title
        self.subtitle = subtitle

    def render(self):
        title = Text(self.title, style=self.get_component_rich_style("title"))
        subtitle = Text(self.subtitle, style=self.get_component_rich_style("subtitle"))

        return title + "\n" + subtitle
