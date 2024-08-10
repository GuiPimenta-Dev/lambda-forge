from textual.app import ComposeResult
from textual.widgets import Input, Select, TextArea

from lambda_forge.live.tui.ui.widgets.text_area_theme import get_text_area

from ._base import TriggerBaseWidget, TriggerBaseContainer


class ApiGatewayContainer(TriggerBaseContainer):
    DEFAULT_CSS = """
    ApiGatewayContainer {
        layout: grid;
        grid-size: 3 2;
        grid-rows: 5 10;
        grid-columns: 1fr 1fr 1fr;
    }

    ApiGatewayContainer > #url {
        column-span: 2;
    }
    """

    METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

    def compose(self) -> ComposeResult:
        yield Select(options=[(i, i) for i in self.METHODS], id="method")
        yield Input(id="url")

        yield get_text_area("query")
        yield get_text_area("body")
        yield get_text_area("headers")


class ApiGateway(TriggerBaseWidget):
    def render_left(self) -> ComposeResult:
        yield ApiGatewayContainer()
