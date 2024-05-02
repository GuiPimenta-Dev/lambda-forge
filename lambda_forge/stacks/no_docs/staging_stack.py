import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from lambda_forge import context, CodeBuildSteps


@context(stage="Staging", resources="staging")
class StagingStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.stage}-{context.name}-Stack", **kwargs)

        source = CodePipelineSource.git_hub(f"{context.repo['owner']}/{context.repo['name']}", "staging")

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
        coverage = steps.coverage()
        validate_docs = steps.validate_docs()
        validate_integration_tests = steps.validate_integration_tests()

        # post
        integration_tests = steps.integration_tests()

        pipeline.add_stage(
            DeployStage(self, context),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[
                integration_tests,
            ],
        )
