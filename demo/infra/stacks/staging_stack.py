import aws_cdk as cdk
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct
from lambda_forge.constants import ECR
from lambda_forge.context import context
from lambda_forge.steps import CodeBuildSteps

from infra.stages.deploy import DeployStage


@context(stage="Staging", resources="staging")
class StagingStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, context.create_id("Stack"), **kwargs)

        source = CodePipelineSource.git_hub(f"{context.repo['owner']}/{context.repo['name']}", "dev")

        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            pipeline_name=context.create_id("Pipeline"),
            synth=pipelines.ShellStep("Synth", input=source, commands=["cdk synth"]),
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.from_docker_registry(ECR.LATEST),
                )
            ),
        )

        steps = CodeBuildSteps(self, context, source=source)

        # pre
        unit_tests = steps.unit_tests()
        coverage = steps.coverage()
        validate_docs = steps.validate_docs()
        validate_integration_tests = steps.validate_integration_tests()
        validate_todo = steps.custom_step(name="ValidateTodo", commands=["cdk synth", "python infra/scripts/validate_todo.py"])

        # post
        redoc = steps.redoc()
        swagger = steps.swagger()
        integration_tests = steps.integration_tests()
        tests_report = steps.tests_report()
        coverage_report = steps.coverage_report()

        pipeline.add_stage(
            DeployStage(self, context),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
                validate_todo
            ],
            post=[
                redoc,
                swagger,
                integration_tests,
                tests_report,
                coverage_report,
            ],
        )
