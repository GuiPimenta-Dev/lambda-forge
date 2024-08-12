from json import JSONDecodeError, loads
from typing import Dict, Optional
from textual.app import ComposeResult, on
from textual.widget import Widget
from textual.widgets import Input, OptionList, Select, Static, TextArea
from lambda_forge.live.trigger_cli import run_trigger
from ._result_window import ResultWindow, RunHistoryItem
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

        data = dict(service=self.service)

        for widget in self.container_widget.children:
            if not widget.id:
                continue

            _id = widget.id

            if isinstance(widget, Input):
                data[_id] = widget.value
            elif isinstance(widget, TextArea):
                try:
                    data[_id] = loads(widget.text)
                except JSONDecodeError:
                    self.notify(f"Invalid JSON for {widget.id}", severity="error")
            elif isinstance(widget, Select):
                data[_id] = str(widget.value) if widget.value != Select.BLANK else ""

        return data

    def _add_history(self, service: str, data: Dict):
        res = self.query_one(ResultWindow)
        data = data | {"service": service}
        res.add_history(data)

    @on(TriggerSubmit.Pressed)
    def _trigger_button_pressed(self, _: TriggerSubmit.Pressed):
        self.run_trigger()

    def run_trigger(self, params: Optional[Dict] = None):
        data = params or self.get_input_values()
        service = data.pop("service")

        try:
            run_trigger(service, data)
            self._add_history(service, data)
        except Exception as e:
            self.notify(str(e), severity="error")

    @on(OptionList.OptionSelected)
    def re_run_trigger(self, event: OptionList.OptionSelected):
        if not isinstance(event.option, RunHistoryItem):
            raise ValueError("Invalid option")

        self.run_trigger(event.option.history)

    def compose(self) -> ComposeResult:
        yield from self.render_left()
        yield ResultWindow()
        yield TriggerSubmit()
