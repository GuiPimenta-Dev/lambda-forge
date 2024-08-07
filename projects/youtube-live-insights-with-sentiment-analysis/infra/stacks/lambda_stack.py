from authorizers.secret.config import SecretAuthorizerConfig
from aws_cdk import Stack
from constructs import Construct
from docs.config import DocsConfig
from functions.chart.chart_worker.config import ChartWorkerConfig
from functions.chart.create_chart.config import CreateChartConfig
from functions.chart.get_chart.config import GetChartConfig
from functions.download.get_chat.config import GetChatConfig
from functions.download.get_video.config import GetVideoConfig
from functions.download.starter.config import StarterConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        SecretAuthorizerConfig(self.services)

        # Docs
        DocsConfig(self.services)

        # Download
        StarterConfig(self.services)
        GetVideoConfig(self.services)
        GetChatConfig(self.services)

        # Chart
        GetChartConfig(self.services)
        ChartWorkerConfig(self.services, self)
        CreateChartConfig(self.services)
