from functions.somewhere.hello_world.config import HelloWorldConfig
from functions.somewhere.hello_world.config import HelloWorldConfig
from functions.somewhere.hello_world.config import HelloWorldConfig
from functions.authorizers.docs.config import DocsConfig
from aws_cdk import Stack
from constructs import Construct
from infra.services import Services


class LambdaStack(Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:

        super().__init__(scope, f"{context.stage}-{context.name}-Lambda-Stack", **kwargs)

        self.services = Services(self, context)

        # Authorizers
        DocsConfig(self.services)

        # Somewhere
        HelloWorldConfig(self.services)
        HelloWorldConfig(self.services)
        HelloWorldConfig(self.services)
