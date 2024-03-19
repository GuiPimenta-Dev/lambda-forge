
import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from infra.steps.code_build_step import CodeBuildStep


class StagingStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").title()
        super().__init__(scope, f"Staging-{name}-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"{repo['owner']}/{repo['name']}", "staging")

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=source,
                install_commands=[
                    "pip install aws-cdk-lib",
                    "npm install -g aws-cdk",
                ],
                commands=[
                    "cdk synth",
                ],
            ),
            pipeline_name=f"Staging-{name}-Pipeline",
        )

        context = self.node.try_get_context("staging")
        stage = "Staging"

        code_build = CodeBuildStep(self, stage, source)

        # pre
        unit_tests = code_build.run_unit_tests()
        coverage = code_build.run_coverage()
        validate_docs = code_build.validate_docs()
        validate_integration_tests = code_build.validate_integration_tests()

        # post
        generate_docs = code_build.generate_docs(name, stage)
        integration_tests = code_build.run_integration_tests()

        pipeline.add_stage(
            DeployStage(self, stage, context["arns"]),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[integration_tests, generate_docs],
        )
