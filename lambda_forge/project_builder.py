from lambda_forge.file_service import FileService


class ProjectBuilder(FileService):
    @staticmethod
    def a_project():
        return ProjectBuilder()

    def __init__(self):
        self.docs = False
        self.dev = None
        self.staging = None
        self.prod = None

    def with_docs(self):
        self.docs = True
        return self

    def with_dev(self):
        self.dev = """
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
"""
        return self

    def with_staging(self):
        self.staging = f"""
import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from infra.steps.code_build_step import CodeBuildStep


class StagingPipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").capitalize()
        super().__init__(scope, f"Staging-{{name}}-Pipeline-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"{{repo["owner"]}}/{{repo["name"]}}", "staging")

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
            pipeline_name=f"Dev-{{name}}-Pipeline",
        )

        context = self.node.try_get_context("staging")
        stage = "Staging"

        code_build = CodeBuildStep(self, stage, source)

        # pre
        unit_tests = code_build.run_unit_tests()
        coverage = code_build.run_coverage()
        validate_docs = code_build.validate_docs()
        validate_integration_tests = code_build.validate_integration_tests()

        # post
        bucket = self.node.try_get_context("docs")["bucket"]
        generate_docs = code_build.generate_docs(name, stage, bucket)
        integration_tests = code_build.run_integration_tests()

        pipeline.add_stage(
            DeployStage(self, stage, context["arns"]),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[integration_tests{", generate_docs" if self.docs else ""}],
        )
"""
        return self

    def with_prod(self):
        self.prod = f"""
import aws_cdk as cdk
from aws_cdk import pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct

from infra.stages.deploy import DeployStage
from infra.steps.code_build_step import CodeBuildStep


class ProdPipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").capitalize()
        super().__init__(scope, f"Prod-{{name}}-Pipeline-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"{{repo["owner"]}}/{{repo["name"]}}", "main")

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
            pipeline_name=f"Prod-{{name}}-Pipeline",
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
        bucket = self.node.try_get_context("docs")["bucket"]
        generate_staging_docs = code_build.generate_docs(name, staging_stage, bucket)
        integration_tests = code_build.run_integration_tests()

        pipeline.add_stage(
            DeployStage(self, staging_stage, staging_context["arns"]),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[generate_staging_docs, integration_tests],
        )

        prod_context = self.node.try_get_context("prod")
        prod_stage = "Prod"

        # post
        generate_prod_docs = code_build.generate_docs(name, prod_stage, bucket)

        pipeline.add_stage(
            DeployStage(self, prod_stage, prod_context["arns"]),
            post=[{"generate_prod_docs" if self.docs else ""}],
        )
"""
        return self

    def with_app(self):
        self.app = ["import aws_cdk as cdk\n"]

        if self.dev:
            self.app.append(
                "from infra.stacks.dev_pipeline_stack import DevPipelineStack\n"
            )

        if self.staging:
            self.app.append(
                "from infra.stacks.staging_pipeline_stack import StagingPipelineStack\n"
            )

        if self.prod:
            self.app.append(
                "from infra.stacks.prod_pipeline_stack import ProdPipelineStack\n"
            )

        self.app.append("\napp = cdk.App()\n\n")

        if self.dev:
            self.app.append("DevPipelineStack = DevPipelineStack(app)\n")

        if self.staging:
            self.app.append("StagingStack = StagingPipelineStack(app)\n")

        if self.prod:
            self.app.append("ProdStack = ProdPipelineStack(app)\n")

        self.app.append("\napp.synth()")
        return self

    def build(self):
        self.copy_folders("/lambda_forge/files", "")
        if self.dev:
            self.make_file("infra/stacks", "dev_pipeline_stack.py", self.dev)

        if self.staging:
            self.make_file("infra/stacks", "staging_pipeline_stack.py", self.staging)

        if self.prod:
            self.make_file("infra/stacks", "prod_pipeline_stack.py", self.prod)

        self.write_lines("app.py", self.app)
