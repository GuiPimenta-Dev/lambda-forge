
import aws_cdk as cdk
from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from infra.steps.code_build_step import CodeBuildStep


class ProdStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").title()
        super().__init__(scope, f"Prod-{name}-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"{repo['owner']}/{repo['name']}", "main")

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
            pipeline_name=f"Prod-{name}-Pipeline",
        )

        staging_context = self.node.try_get_context("staging")
        staging_stage = "Staging"

        code_build = CodeBuildStep(self, staging_stage, source)

        # pre
        unit_tests = code_build.run_unit_tests()
        coverage = code_build.run_coverage()
        validate_docs = code_build.validate_docs()
        validate_integration_tests = code_build.validate_integration_tests()

        # post
        generate_staging_docs = code_build.generate_docs(name, staging_stage)
        integration_tests = code_build.run_integration_tests()

        pipeline.add_stage(
            DeployStage(self, staging_stage, staging_context["arns"]),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[integration_tests, generate_staging_docs],
        )

        prod_context = self.node.try_get_context("prod")
        prod_stage = "Prod"

        # post
        generate_prod_docs = code_build.generate_docs(name, prod_stage)

        pipeline.add_stage(
            DeployStage(self, prod_stage, prod_context["arns"]),
            post=[generate_prod_docs],
        )
