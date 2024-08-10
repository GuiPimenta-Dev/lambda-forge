from textual.app import ComposeResult
from textual.widgets import Input

from lambda_forge.live.tui.ui.widgets.text_area_theme import get_text_area

from ._base import TriggerBaseWidget, TriggerBaseContainer


class EventBridgeContainer(TriggerBaseContainer):
    DEFAULT_CSS = """
    EventBridgeContainer {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 5 10;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(id="bus_name")
        yield get_text_area("message")


class EventBridge(TriggerBaseWidget):
    def render_left(self) -> ComposeResult:
        yield EventBridgeContainer()
