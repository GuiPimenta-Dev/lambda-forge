from textual.widgets import Button


class TriggerSubmit(Button):

    def on_click(self):
        if not self.parent:
            raise ValueError("TriggerSubmit must be a child of a form")

        from ._base import TriggerBaseWidget

        if not isinstance(self.parent, TriggerBaseWidget):
            raise ValueError("Container not found")

        from ._result_window import ResultWindow

        res = self.parent.query_one(ResultWindow)
        values = self.parent.get_input_values()

        res.add_history(values)
