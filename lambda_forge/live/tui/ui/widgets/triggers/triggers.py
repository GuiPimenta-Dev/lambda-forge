from textual.app import ComposeResult
from textual.widgets import Static, TabPane, TabbedContent
from .s3 import S3
from .sns import SNS
from .sqs import SQS
from .event_bridge import EventBridge
from .api_gateway import ApiGateway


class Triggers(Static):

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Api Gateway", id="api_gateway"):
                yield ApiGateway()

            with TabPane("EventBridge", id="event_bridge"):
                yield EventBridge()

            with TabPane("SNS", id="sns"):
                yield SNS()

            with TabPane("SQS", id="sqs"):
                yield SQS()

            with TabPane("S3", id="s3"):
                yield S3()
