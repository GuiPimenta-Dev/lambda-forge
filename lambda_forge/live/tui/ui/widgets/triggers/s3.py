from textual.app import ComposeResult
from textual.widgets import Input, TextArea

from lambda_forge.live.tui.ui.widgets.text_area_theme import get_text_area

from ._base import TriggerBaseWidget, TriggerBaseContainer


class S3Container(TriggerBaseContainer):
    DEFAULT_CSS = """
    S3Container {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 5 10;
        grid-columns: 1fr 1fr;

        TextArea {
            column-span: 2;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(id="bucket_name")
        yield Input(id="file_path")
        yield get_text_area("metadata")


class S3(TriggerBaseWidget):
    service = "S3"

    def render_left(self) -> ComposeResult:
        yield S3Container()
