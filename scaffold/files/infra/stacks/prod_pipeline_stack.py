import aws_cdk as cdk
from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from infra.steps.code_build_step import CodeBuildStep


class ProdPipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").capitalize()
        super().__init__(scope, f"Prod{name}PipelineStack", **kwargs)

        repo_name = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"GuiPimenta-Dev/{repo_name}", "master")

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

        dev_context = self.node.try_get_context("dev")
        dev_stage = "Dev"

        code_build = CodeBuildStep(self, dev_stage, source)

        # pre
        unit_tests = code_build.run_unit_tests()
        coverage = code_build.run_coverage()
        validate_docs = code_build.validate_docs()
        validate_integration_tests = code_build.validate_integration_tests()

        # post
        generate_dev_docs = code_build.generate_docs(name, dev_stage)
        integration_tests = code_build.run_integration_tests()

        pipeline.add_stage(
            DeployStage(self, dev_stage, dev_context["arns"]),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[generate_dev_docs, integration_tests],
        )

        prod_context = self.node.try_get_context("prod")
        prod_stage = "Prod"

        # post
        generate_prod_docs = code_build.generate_docs(name, prod_stage)

        pipeline.add_stage(
            DeployStage(
                self, prod_stage, prod_context["arns"], alarms=False, versioning=True
            ),
            post=[generate_prod_docs],
        )
