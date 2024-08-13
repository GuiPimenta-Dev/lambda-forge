from textual.widget import Widget
from ...api.forge_logs import LambdaGroup


class CloudWatchLogs(Widget):
    def __init__(self, log_group: LambdaGroup):
        self.log_group = log_group
        super().__init__(id=log_group.name.replace("/", "-"))
