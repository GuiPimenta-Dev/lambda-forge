from typing import Dict
from textual.app import ComposeResult, on
from textual.widget import Widget
from textual.widgets import Input, Select, Static, TextArea
from ._result_window import ResultWindow
from ._trigger_submit import TriggerSubmit


class TriggerBaseContainer(Widget):
    DEFAULT_CSS = """
    TriggerBaseContainer {
        height: 1fr;
    }
    """


class TriggerBaseWidget(Static):
    DEFAULT_CSS = """
    TriggerBaseWidget {
        layout: grid;
        grid-size: 2 2;
        grid-columns: 5fr 2fr;
        grid-rows: 1fr 4;
        height: 1fr;
    }

    TriggerBaseWidget {
        ResultWindow {
            row-span: 2;
        }

        TriggerSubmit {
            margin-top: 1;
            margin-left: 1;
            margin-right: 1;
            width: 100%;
        }
    } 
    """

    @property
    def container_widget(self) -> TriggerBaseContainer:
        if not self.parent:
            raise ValueError("Parent not set")

        return self.parent.query_one(TriggerBaseContainer)

    def on_mount(self) -> None:
        for i in self.container_widget.children:
            if not i.id:
                continue

            i.border_title = i.id
            i.border_title_align = "center"

    def render_left(self) -> ComposeResult:
        yield from []

    def get_input_values(self) -> Dict:
        if not self.parent:
            return {}

        data = {}

        for widget in self.container_widget.children:
            if not widget.id:
                continue

            _id = widget.id

            if isinstance(widget, Input):
                data[_id] = widget.value
            elif isinstance(widget, TextArea):
                data[_id] = widget.text
            elif isinstance(widget, Select):
                data[_id] = widget.value

        return data

    @on(TriggerSubmit.Pressed)
    def run_trigger(self, event: TriggerSubmit.Pressed):
        data = self.get_input_values()
        self.notify(str(data))

    def compose(self) -> ComposeResult:
        yield from self.render_left()
        yield ResultWindow()
        yield TriggerSubmit()
