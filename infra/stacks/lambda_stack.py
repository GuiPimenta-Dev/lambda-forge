from functions.docs.config import DocsConfig
from functions.authorizers.docs_authorizer.config import DocsAuthorizerConfig
from aws_cdk import Stack
from constructs import Construct
from infra.services import Services


class LambdaStack(Stack):
    def __init__(
        self,
        scope: Construct,
        context,
        **kwargs,
    ) -> None:

        name = scope.node.try_get_context("name")
        super().__init__(scope, f"{name}-CDK", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        DocsAuthorizerConfig(self.services)

        # Docs
        DocsConfig(scope, self.services)
