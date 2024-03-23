from authorizers.docs.config import DocsAuthorizerConfig
from aws_cdk import Stack
from constructs import Construct
from infra.services import Services
from lambda_forge import release


@release
class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-CDK", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        DocsAuthorizerConfig(self.services)
