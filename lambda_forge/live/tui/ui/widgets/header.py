from rich.text import Text
from textual.widget import Widget


class ForgeHeader(Widget):
    DEFAULT_CSS = """
    ForgeHeader {
        padding: 1 4;
    }
    """

    COMPONENT_CLASSES = {"title", "subtitle"}

    def __init__(
        self,
        title: str = "λ Lambda Forge",
        subtitle: str = "Simplify AWS Lambda deployments",
    ):
        super().__init__()
        self.title = title
        self.subtitle = subtitle

    def render(self):
        title = Text(self.title, style=self.get_component_rich_style("title"))
        subtitle = Text(self.subtitle, style=self.get_component_rich_style("subtitle"))

        return title + "\n" + subtitle
