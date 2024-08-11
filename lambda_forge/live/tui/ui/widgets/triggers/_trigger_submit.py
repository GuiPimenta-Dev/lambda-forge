from rich.console import RenderableType
from textual.widgets import Button


class TriggerSubmit(Button):
    def render(self) -> RenderableType:
        return "Submit"
