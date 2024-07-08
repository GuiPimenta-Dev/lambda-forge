from authorizers.secret.config import SecretAuthorizerConfig
from aws_cdk import Stack
from constructs import Construct
from docs.config import DocsConfig
from functions.custom.config import CustomConfig
from functions.external.config import ExternalConfig
from functions.hello_world.config import HelloWorldConfig
from functions.private.config import PrivateConfig
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        SecretAuthorizerConfig(self.services)

        # Docs
        DocsConfig(self.services)

        # HelloWorld
        HelloWorldConfig(self.services)

        # # Private
        PrivateConfig(self.services)

        # Custom
        CustomConfig(self.services)

        # # External
        ExternalConfig(self.services)
