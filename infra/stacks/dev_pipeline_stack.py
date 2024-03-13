
import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct
from infra.stages.deploy import DeployStage


class DevPipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").capitalize()
        super().__init__(scope, f"Dev-{name}-Pipeline-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"{repo["owner"]}/{repo["name"]}", "dev")

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
            pipeline_name=f"Playground-{name}-Pipeline",
        )

        context = self.node.try_get_context("dev")
        stage = "Dev"

        pipeline.add_stage(DeployStage(self, stage, context["arns"]))
