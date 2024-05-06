from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct


class CodePipeline:
    def __init__(self, scope: Construct, context, branch, install_commands=[], commands=[]) -> None:

        self.source = CodePipelineSource.git_hub(f"{context.repo['owner']}/{context.repo['name']}", branch)

        self.pipeline = pipelines.CodePipeline(
            scope,
            "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=self.source,
                install_commands=[
                    "pip install lambda-forge --extra-index-url https://pypi.org/simple --extra-index-url https://test.pypi.org/simple/",
                    "pip install aws-cdk-lib",
                    "npm install -g aws-cdk",
                    *install_commands,
                ],
                commands=["cdk synth", *commands],
            ),
            pipeline_name=f"{context.stage}-{context.name}-Pipeline",
        )

    def add_stage(self, stage):
        self.pipeline.add_stage(stage)
