from typing import Dict, Optional
from textual.app import App
from .screens import Index
from ..api import ForgeLogsAPI


class ForgeLogsApp(App):

    def __init__(self, params: Optional[Dict]):
        super().__init__()
        self.logs_api = ForgeLogsAPI(params)

    def on_mount(self) -> None:
        self.push_screen(Index())
