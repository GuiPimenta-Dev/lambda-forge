import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from constructs import Construct
from infra.stages.deploy import DeployStage

from lambda_forge import context
from lambda_forge.services import CodeBuildSteps, CodePipeline


@context(stage="Staging", resources="staging")
class StagingStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.stage}-{context.name}-Stack", **kwargs)

        pipeline = CodePipeline(self, context, branch="staging")

        steps = CodeBuildSteps(self, context, source=pipeline.source)

        # pre
        unit_tests = steps.unit_tests()
        coverage = steps.coverage()
        validate_docs = steps.validate_docs()
        validate_integration_tests = steps.validate_integration_tests()

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
            ],
            post=[
                redoc,
                swagger,
                integration_tests,
                tests_report,
                coverage_report,
            ],
        )
