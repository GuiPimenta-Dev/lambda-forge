import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from constructs import Construct
from infra.stages.deploy import DeployStage

from lambda_forge import context
from lambda_forge.services import CodePipeline


@context(stage="Dev", resources="dev")
class DevStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.stage}-{context.name}-Stack", **kwargs)

        pipeline = CodePipeline(self, context, branch="dev")

        pipeline.add_stage(DeployStage(self, context))
