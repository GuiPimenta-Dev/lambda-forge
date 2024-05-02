import aws_cdk as cdk
from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from lambda_forge import context, CodeBuildSteps


@context(stage="Prod", resources="prod")
class ProdStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.stage}-{context.name}-Stack", **kwargs)

        source = CodePipelineSource.git_hub(f"{context.repo['owner']}/{context.repo['name']}", "main")

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=source,
                install_commands=[
                    "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                    "pip install aws-cdk-lib",
                    "npm install -g aws-cdk",
                ],
                commands=[
                    "cdk synth",
                ],
            ),
            pipeline_name=f"{context.stage}-{context.name}-Pipeline",
        )

        steps = CodeBuildSteps(self, context, source)

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
