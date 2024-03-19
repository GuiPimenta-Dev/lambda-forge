
import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct
from infra.stages.deploy import DeployStage
from lambda_forge import Steps


class DevStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").title()
        # name = ""
        super().__init__(scope, f"Dev-{name}-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        # repo = {
            # "owner": "asd",
            # "name": "das",
        # }
        source = CodePipelineSource.git_hub(f"{repo['owner']}/{repo['name']}", "dev")

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
            pipeline_name=f"Dev-{name}-Pipeline",
        )

        # context = self.node.try_get_context("dev")
        context = {"arns": ""}
        stage = "Dev"

        steps= Steps(scope, stage, source)
        validate_integration_tests = steps.validate_integration_tests()
        generate_docs = steps.generate_docs(name, stage)


        pipeline.add_stage(DeployStage(self, stage, context["arns"]), pre=[validate_integration_tests, generate_docs])
