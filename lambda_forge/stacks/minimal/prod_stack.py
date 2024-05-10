import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct
from infra.stages.deploy import DeployStage

from lambda_forge.constants import ECR
from lambda_forge.context import context


@context(stage="Prod", resources="prod")
class ProdStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.stage}-{context.name}-Stack", **kwargs)

        source = CodePipelineSource.git_hub(f"{context.repo['owner']}/{context.repo['name']}", "dev")

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            pipeline_name=f"{context.stage}-{context.name}-Pipeline",
            synth=pipelines.ShellStep("Synth", input=source, commands=["cdk synth"]),
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.from_docker_registry(ECR.LATEST),
                )
            ),
        )

        pipeline.add_stage(DeployStage(self, context))
