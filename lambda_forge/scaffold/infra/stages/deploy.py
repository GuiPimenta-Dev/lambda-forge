import aws_cdk as cdk
from constructs import Construct

from infra.stacks.lambda_stack import LambdaStack


class DeployStage(cdk.Stage):
    def __init__(self, scope: Construct, context, **kwargs):
        super().__init__(scope, context.stage, **kwargs)

        ls = LambdaStack(self, context)

        ls.services.api_gateway.create_docs(authorizer="docs")
