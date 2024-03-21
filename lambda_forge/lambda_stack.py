from aws_cdk import Stack
from constructs import Construct


class LambdaStack(Stack):
    def __init__(
        self,
        scope: Construct,
        context,
        services,
        authorizers,
        functions,
        docs,
        docs_authorizer,
        **kwargs,
    ) -> None:

        super().__init__(scope, f"{context.name}-CDK", **kwargs)
