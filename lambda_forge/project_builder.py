from lambda_forge.file_service import FileService
import json

# from file_service import FileService
# from lambda_forge.function_builder import FunctionBuilder


class ProjectBuilder(FileService):
    @staticmethod
    def a_project(name, docs):
        return ProjectBuilder(name, docs)

    def __init__(self, name, docs):
        self.name = name
        self.docs = docs
        self.dev = None
        self.staging = None
        self.prod = None

    def with_dev(self):
        self.dev = """
import aws_cdk as cdk
from aws_cdk import pipelines as pipelines
from aws_cdk.pipelines import CodePipelineSource
from constructs import Construct
from infra.stages.deploy import DeployStage


class DevPipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        name = scope.node.try_get_context("name").title()
        super().__init__(scope, f"Dev-{name}-Pipeline-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
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
        name = scope.node.try_get_context("name").title()
        super().__init__(scope, f"Staging-{{name}}-Pipeline-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"{{repo['owner']}}/{{repo['name']}}", "staging")

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
            pipeline_name=f"Staging-{{name}}-Pipeline",
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
        generate_docs = code_build.generate_docs(name, stage)
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
        name = scope.node.try_get_context("name").title()
        super().__init__(scope, f"Prod-{{name}}-Pipeline-Stack", **kwargs)

        repo = self.node.try_get_context("repo")
        source = CodePipelineSource.git_hub(f"{{repo['owner']}}/{{repo['name']}}", "main")

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
        generate_staging_docs = code_build.generate_docs(name, staging_stage)
        integration_tests = code_build.run_integration_tests()

        pipeline.add_stage(
            DeployStage(self, staging_stage, staging_context["arns"]),
            pre=[
                unit_tests,
                coverage,
                validate_integration_tests,
                validate_docs,
            ],
            post=[integration_tests{", generate_staging_docs" if self.docs else ""}],
        )

        prod_context = self.node.try_get_context("prod")
        prod_stage = "Prod"

        # post
        generate_prod_docs = code_build.generate_docs(name, prod_stage)

        pipeline.add_stage(
            DeployStage(self, prod_stage, prod_context["arns"]),
            post=[{"generate_prod_docs" if self.docs else ""}],
        )
"""
        return self

    def with_cdk(self, repo_owner, repo_name, bucket):
        cdk = {
            "app": "python3 app.py",
            "watch": {
                "include": ["**"],
                "exclude": [
                    "README.md",
                    "cdk*.json",
                    "requirements*.txt",
                    "source.bat",
                    "**/__init__.py",
                    "python/__pycache__",
                    "tests",
                ],
            },
            "context": {
                "@aws-cdk/aws-lambda:recognizeLayerVersion": True,
                "@aws-cdk/core:checkSecretUsage": True,
                "@aws-cdk/core:target-partitions": ["aws", "aws-cn"],
                "@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver": True,
                "@aws-cdk/aws-ec2:uniqueImdsv2TemplateName": True,
                "@aws-cdk/aws-ecs:arnFormatIncludesClusterName": True,
                "@aws-cdk/aws-iam:minimizePolicies": True,
                "@aws-cdk/core:validateSnapshotRemovalPolicy": True,
                "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": True,
                "@aws-cdk/aws-s3:createDefaultLoggingPolicy": True,
                "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": True,
                "@aws-cdk/aws-apigateway:disableCloudWatchRole": True,
                "@aws-cdk/core:enablePartitionLiterals": True,
                "@aws-cdk/aws-events:eventsTargetQueueSameAccount": True,
                "@aws-cdk/aws-iam:standardizedServicePrincipals": True,
                "@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker": True,
                "@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName": True,
                "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": True,
                "@aws-cdk/aws-route53-patters:useCertificate": True,
                "@aws-cdk/customresources:installLatestAwsSdkDefault": False,
                "region": "us-east-2",
                "account": "",
                "name": self.name.title(),
                "repo": {"owner": repo_owner, "name": repo_name},
                "bucket": bucket,
                "dev": {"arns": {}},
                "staging": {"arns": {}},
                "prod": {"arns": {}},
            },
        }

        self.cdk = json.dumps(cdk, indent=2)
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
        self.copy_folders("lambda_forge", "files", "")

        if self.dev:
            self.make_file(
                f"{self.root_dir}/infra/stacks", "dev_pipeline_stack.py", self.dev
            )

        if self.staging:
            self.make_file(
                f"{self.root_dir}/infra/stacks",
                "staging_pipeline_stack.py",
                self.staging,
            )

        if self.prod:
            self.make_file(
                f"{self.root_dir}/infra/stacks", "prod_pipeline_stack.py", self.prod
            )

        self.make_file("", "cdk.json", self.cdk)
        self.write_lines("app.py", self.app)
