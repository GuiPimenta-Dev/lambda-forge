from functions.crawler.config import CrawlerConfig
from aws_cdk import Stack
from constructs import Construct

from functions.start.config import StartConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Start
        StartConfig(self.services)

        # Crawler
        CrawlerConfig(self.services)
