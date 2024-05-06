import aws_cdk as cdk
from constructs import Construct
from infra.stages.deploy import DeployStage

from lambda_forge import context
from lambda_forge.services import CodeBuildSteps, CodePipeline


@context(stage="Prod", resources="prod")
class ProdStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.stage}-{context.name}-Stack", **kwargs)

        pipeline = CodePipeline(self, context, branch="main")

        steps = CodeBuildSteps(self, context, source=pipeline.source)

        # pre
        unit_tests = steps.unit_tests()
        integration_tests = steps.integration_tests()

        # post
        diagram = steps.diagram()
        redoc = steps.redoc()
        swagger = steps.swagger()

        pipeline.add_stage(
            DeployStage(self, context),
            pre=[
                unit_tests,
                integration_tests,
            ],
            post=[
                diagram,
                redoc,
                swagger,
            ],
        )
