from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import LoadingIndicator


class LoadingScreen(Screen):

    async def on_mount(self):
        self.is_syntesis_complete = False
        self.init_forge()
        self.synth_check_timer = self.set_interval(0.5, self.check_for_synthesis)

    @work(thread=True)
    async def init_forge(self):

        # TODO: Your code here
        # from time import sleep
        # sleep(2)

        self.is_syntesis_complete = True

    def check_for_synthesis(self):
        if self.is_syntesis_complete:
            self.synth_check_timer.stop()
            self.dismiss_screen()

    def dismiss_screen(self):
        self.app.pop_screen()
        self.app.push_screen("index")

    def compose(self) -> ComposeResult:
        yield LoadingIndicator()
