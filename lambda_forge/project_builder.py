from lambda_forge.file_service import FileService
import json


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


class DevStack(cdk.Stack):
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


class StagingStack(cdk.Stack):
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


class ProdStack(cdk.Stack):
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

    def with_gitignore(self):
        self.gitignore = """
# Compiled source #
###################
*.swp

# Packages #
############
# It's generally good practice to exclude package lock files to prevent conflicts between different environments
package-lock.json

# Python bytecode #
###################
__pycache__/
*.py[cod]

# Pytest cache #
################
.pytest_cache/

# Virtual Environment #
#######################
.venv/
venv/
env/

# Distribution / packaging #
############################
*.egg-info/
dist/
build/

# PyInstaller #
##############
# Usually, you don't track these files but depends on the project
# If you're using PyInstaller, uncomment the next line
# *.spec

# Installer logs #
##################
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports #
################################
htmlcov/
.coverage
.coverage.*
.coverage_e2e
cov.xml
coverage.xml
nosetests.xml
junit.xml

# Translations #
################
*.mo
*.pot

# Django stuff: #
#################
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff: #
################
instance/
.webassets-cache

# Scrapy stuff: #
#################
.scrapy

# Sphinx documentation #
########################
docs/_build/

# PyBuilder #
#############
target/

# Jupyter Notebook #
####################
.ipynb_checkpoints

# pyenv #
#########
.python-version

# celery beat schedule file #
#############################
celerybeat-schedule

# SageMath parsed files #
#########################
*.sage.py

# dotenv #
##########
.env

# Spyder project settings #
###########################
.spyderproject
.spyproject

# Rope project settings #
#########################
.ropeproject

# mkdocs documentation #
########################
/site

# mypy #
########
.mypy_cache/

# Databases #
#############
*.db
*.sql
*.sqlite

# Backup files #
################
*.bak

# If you're using IntelliJ products (e.g., PyCharm), you might want to ignore these #
#####################################################################################
.idea/
*.iml

# Visual Studio Code #
######################
.vscode/

# CDK asset staging directory #
###############################
.cdk.staging
cdk.out

# Misc #
#######
.DS_Store

# Documentation files #
#######################
docs.yaml

# Lambda Forge Stuff #
###############
.fc
sam.out
.tested_endpoints.jsonl

# Coverage reports #
####################
coverage.xml
"""
        return self

    def with_pre_commit(self):
        self.pre_commit = """
fail_fast: true

repos:
  - repo: local
    hooks:
      - id: cdk
        name: remove cdk.out
        entry: rm -rf cdk.out
        language: system
        pass_filenames: false
        stages: [commit]
      - id: unit_test
        name: unit tests
        entry: coverage run -m pytest -k 'unit.py'
        language: system
        pass_filenames: false
        stages: [commit]
      - id: coverage
        name: coverage
        entry: coverage report --fail-under=80
        language: system
        pass_filenames: false
        stages: [commit]
      - id: validate_docs
        name: validate docs
        entry: python validate_docs.py
        language: system
        pass_filenames: false
        stages: [commit]
      - id: generate_docs
        name: generate docs
        entry: python generate_docs.py
        language: system
        pass_filenames: false
        stages: [commit]
      - id: validate_integration
        name: validate integration tests
        entry: python validate_integration_tests.py
        language: system
        pass_filenames: false
        stages: [commit]
      - id: cleaning
        name: cleaning
        entry: rm -rf .fc coverage.xml .coverage .tested_endpoints.jsonl htmlcov .DS_Store build/ gaia.egg-info/ docs.yaml
        language: system
        pass_filenames: false
        stages: [commit]
"""
        return self

    def with_coverage(self):
        self.coverage = """
[run]
branch = True
include =
    functions/**/main.py
    functions/**/utils.py

omit=
"""
        return self

    def with_cdk(self, repo_owner, repo_name, bucket, coverage):
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
                "name": self.name.title().replace("_", "-").replace(" ", "-"),
                "repo": {"owner": repo_owner, "name": repo_name},
                "bucket": bucket,
                "coverage": coverage,
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
            self.app.append("from infra.stacks.dev_stack import DevStack\n")

        if self.staging:
            self.app.append("from infra.stacks.staging_stack import StagingStack\n")

        if self.prod:
            self.app.append("from infra.stacks.prod_stack import ProdStack\n")

        self.app.append("\napp = cdk.App()\n\n")

        if self.dev:
            self.app.append("DevStack = DevStack(app)\n")

        if self.staging:
            self.app.append("StagingStack = StagingStack(app)\n")

        if self.prod:
            self.app.append("ProdStack = ProdStack(app)\n")

        self.app.append("\napp.synth()")
        return self

    def build(self):
        self.copy_folders("lambda_forge", "files", "")
        self.make_file("", ".gitignore", self.gitignore)
        self.make_file("", ".pre-commit-config.yaml", self.pre_commit)
        self.make_file("", ".coveragerc", self.coverage)

        if self.dev:
            self.make_file(f"{self.root_dir}/infra/stacks", "dev_stack.py", self.dev)

        if self.staging:
            self.make_file(
                f"{self.root_dir}/infra/stacks",
                "staging_stack.py",
                self.staging,
            )

        if self.prod:
            self.make_file(f"{self.root_dir}/infra/stacks", "prod_stack.py", self.prod)

        self.make_file("", "cdk.json", self.cdk)
        self.write_lines("app.py", self.app)
