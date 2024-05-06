from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct
from aws_cdk import aws_codebuild as codebuild


class CodePipeline:
    def __init__(
        self,
        scope: Construct,
        context,
        branch,
        install_commands=[],
        commands=[],
        registry="public.ecr.aws/x8r4y7j7/lambda-forge:latest",
    ) -> None:
        
        if "cdk synth" not in commands:
            commands.append("cdk synth")

        self.source = CodePipelineSource.git_hub(f"{context.repo['owner']}/{context.repo['name']}", branch)

        self.pipeline = pipelines.CodePipeline(
            scope,
            "Pipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=self.source,
                install_commands=[*install_commands],
                commands=[*commands],
            ),
            pipeline_name=f"{context.stage}-{context.name}-Pipeline",
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.from_docker_registry(registry),
                    privileged=True,
                    compute_type=codebuild.ComputeType.SMALL,
                ),
                cache=codebuild.Cache.local(codebuild.LocalCacheMode.DOCKER_LAYER, codebuild.LocalCacheMode.CUSTOM),
            ),
        )

    def add_stage(self, stage, pre=[], post=[]):
        self.pipeline.add_stage(stage, pre=pre, post=post)
