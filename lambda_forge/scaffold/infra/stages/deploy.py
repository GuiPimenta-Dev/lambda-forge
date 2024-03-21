import aws_cdk as cdk
from constructs import Construct

from infra.stacks.lambda_stack import LambdaStack


class DeployStage(cdk.Stage):
    def __init__(self, scope: Construct, stage: str, arns, **kwargs):
        super().__init__(scope, stage, **kwargs)

        LambdaStack(self, stage, arns)
