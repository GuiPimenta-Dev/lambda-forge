from textual.app import ComposeResult
from textual.widgets import Input
from ._base import TriggerBaseWidget, TriggerBaseContainer
from ..text_area_theme import get_text_area


class SNSContainer(TriggerBaseContainer):
    DEFAULT_CSS = """
    SNSContainer {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 5 10;
        grid-columns: 1fr 1fr;

        Input {
            column-span: 2;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(id="topic_arn")
        yield get_text_area("message")
        yield get_text_area("subject")


class SNS(TriggerBaseWidget):
    service = "SNS"

    def render_left(self) -> ComposeResult:
        yield SNSContainer()
