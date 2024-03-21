import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from lambda_forge import context, Steps

@context(stage="Staging", resources="staging")
class StagingStack(cdk.Stack):
    def __init__(self, scope: Construct, context, **kwargs) -> None:
        super().__init__(scope, f"{context.stage}-{context.name}-Stack", **kwargs)
        
        source = CodePipelineSource.git_hub(f"{context.repo['owner']}/{context.repo['name']}", "staging")

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
            pipeline_name=f"{context.stage}-{context.name}-Pipeline",
        )

        steps = Steps(self, context, source)

        # pre
        unit_tests = steps.run_unit_tests()
        coverage = steps.run_coverage()
        validate_docs = steps.validate_docs()
        validate_integration_tests = steps.validate_integration_tests()

        # post
        generate_docs = steps.generate_docs()
        integration_tests = steps.run_integration_tests()

        pipeline.add_stage(
            DeployStage(self, context),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[integration_tests, generate_docs],
        )
