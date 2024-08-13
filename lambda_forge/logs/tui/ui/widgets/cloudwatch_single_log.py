from textual.widgets.option_list import Option
from ...api.forge_logs import CloudWatchLog


class CloudWatchSingleLog(Option):

    def __init__(self, log: CloudWatchLog):
        super().__init__("")
        self.log = log
        self.set_prompt(str(self.log.timestamp))
