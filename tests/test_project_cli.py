from click.testing import CliRunner
from pprint import pprint
from lambda_forge.main import project
from tests.conftest import read_file_lines, list_files

runner = CliRunner()


def test_it_should_raise_an_error_when_bucket_is_none_and_no_doc_is_false():

    result = runner.invoke(
        project, ["project_name", "--repo-owner", "owner", "--repo-name", "repo"]
    )

    assert (
        result.output
        == "Usage: project [OPTIONS] NAME\nTry 'project --help' for help.\n\nError: You must provide a S3 bucket for the docs or use the flag --no-docs\n"
    )


def test_it_should_not_create_dev_stack_when_no_dev_is_true():

    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-dev",
            "--bucket",
            "bucket",
        ],
    )

    app = read_file_lines("app.py")
    assert app == [
        "import aws_cdk as cdk",
        "from infra.stacks.staging_stack import StagingStack",
        "from infra.stacks.prod_stack import ProdStack",
        "",
        "app = cdk.App()",
        "",
        "StagingStack = StagingStack(app)",
        "ProdStack = ProdStack(app)",
        "",
        "app.synth()",
    ]


def test_it_should_not_create_staging_stack_when_no_staging_is_true():

    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-staging",
            "--bucket",
            "bucket",
        ],
    )

    app = read_file_lines("app.py")
    assert app == [
        "import aws_cdk as cdk",
        "from infra.stacks.dev_stack import DevStack",
        "from infra.stacks.prod_stack import ProdStack",
        "",
        "app = cdk.App()",
        "",
        "DevStack = DevStack(app)",
        "ProdStack = ProdStack(app)",
        "",
        "app.synth()",
    ]


def test_it_should_not_create_prod_stack_when_no_prod_is_true():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-prod",
            "--bucket",
            "bucket",
        ],
    )
    app = read_file_lines("app.py")
    assert app == [
        "import aws_cdk as cdk",
        "from infra.stacks.dev_stack import DevStack",
        "from infra.stacks.staging_stack import StagingStack",
        "",
        "app = cdk.App()",
        "",
        "DevStack = DevStack(app)",
        "StagingStack = StagingStack(app)",
        "",
        "app.synth()",
    ]


def test_it_should_add_the_cdk_json_file():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--bucket",
            "bucket",
        ],
    )
    cdk = read_file_lines("cdk.json")
    assert cdk == [
        "{",
        '  "app": "python3 app.py",',
        '  "watch": {',
        '    "include": [',
        '      "**"',
        "    ],",
        '    "exclude": [',
        '      "README.md",',
        '      "cdk*.json",',
        '      "requirements*.txt",',
        '      "source.bat",',
        '      "**/__init__.py",',
        '      "python/__pycache__",',
        '      "tests"',
        "    ]",
        "  },",
        '  "context": {',
        '    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,',
        '    "@aws-cdk/core:checkSecretUsage": true,',
        '    "@aws-cdk/core:target-partitions": [',
        '      "aws",',
        '      "aws-cn"',
        "    ],",
        '    "@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver": '
        "true,",
        '    "@aws-cdk/aws-ec2:uniqueImdsv2TemplateName": true,',
        '    "@aws-cdk/aws-ecs:arnFormatIncludesClusterName": true,',
        '    "@aws-cdk/aws-iam:minimizePolicies": true,',
        '    "@aws-cdk/core:validateSnapshotRemovalPolicy": true,',
        '    "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": '
        "true,",
        '    "@aws-cdk/aws-s3:createDefaultLoggingPolicy": true,',
        '    "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": true,',
        '    "@aws-cdk/aws-apigateway:disableCloudWatchRole": true,',
        '    "@aws-cdk/core:enablePartitionLiterals": true,',
        '    "@aws-cdk/aws-events:eventsTargetQueueSameAccount": true,',
        '    "@aws-cdk/aws-iam:standardizedServicePrincipals": true,',
        '    "@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker": '
        "true,",
        '    "@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName": true,',
        '    "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": true,',
        '    "@aws-cdk/aws-route53-patters:useCertificate": true,',
        '    "@aws-cdk/customresources:installLatestAwsSdkDefault": false,',
        '    "region": "us-east-2",',
        '    "account": "",',
        '    "name": "Project-Name",',
        '    "repo": {',
        '      "owner": "owner",',
        '      "name": "repo"',
        "    },",
        '    "bucket": "bucket",',
        '    "dev": {',
        '      "arns": {}',
        "    },",
        '    "staging": {',
        '      "arns": {}',
        "    },",
        '    "prod": {',
        '      "arns": {}',
        "    }",
        "  }",
        "}",
    ]


def test_it_should_create_the_files_when_asking_for_docs():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--bucket",
            "bucket",
        ],
    )
    files = list_files(".")
    assert files == [
        "./generate_docs.py",
        "./conftest.py",
        "./pytest.ini",
        "./requirements.txt",
        "./.pre-commit-config.yaml",
        "./cdk.context.json",
        "./cdk.json",
        "./__init__.py",
        "./.coveragerc",
        "./source.bat",
        "./validate_docs.py",
        "./swagger_yml_to_ui.py",
        "./.gitignore",
        "./app.py",
        "./validate_integration_tests.py",
        "./infra/__init__.py",
        "./infra/stacks/staging_stack.py",
        "./infra/stacks/lambda_stack.py",
        "./infra/stacks/__init__.py",
        "./infra/stacks/prod_stack.py",
        "./infra/stacks/dev_stack.py",
        "./infra/stages/__init__.py",
        "./infra/steps/__init__.py",
        "./infra/steps/code_build_step.py",
        "./infra/services/api_gateway.py",
        "./infra/services/aws_lambda.py",
        "./infra/services/__init__.py",
        "./functions/__init__.py",
        "./functions/docs/config.py",
        "./functions/docs/__init__.py",
        "./functions/authorizers/__init__.py",
        "./functions/authorizers/docs_authorizer/config.py",
        "./functions/authorizers/docs_authorizer/__init__.py",
        "./functions/authorizers/docs_authorizer/unit.py",
        "./functions/authorizers/docs_authorizer/main.py",
        "./functions/authorizers/utils/__init__.py",
    ]


def test_it_should_create_the_files_when_not_asking_for_docs():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-docs",
        ],
    )
    files = list_files(".")

    assert files == [
        "./generate_docs.py",
        "./conftest.py",
        "./pytest.ini",
        "./requirements.txt",
        "./.pre-commit-config.yaml",
        "./cdk.context.json",
        "./cdk.json",
        "./__init__.py",
        "./.coveragerc",
        "./source.bat",
        "./validate_docs.py",
        "./swagger_yml_to_ui.py",
        "./.gitignore",
        "./app.py",
        "./validate_integration_tests.py",
        "./infra/__init__.py",
        "./infra/stacks/staging_stack.py",
        "./infra/stacks/lambda_stack.py",
        "./infra/stacks/__init__.py",
        "./infra/stacks/prod_stack.py",
        "./infra/stacks/dev_stack.py",
        "./infra/stages/__init__.py",
        "./infra/steps/__init__.py",
        "./infra/steps/code_build_step.py",
        "./infra/services/api_gateway.py",
        "./infra/services/aws_lambda.py",
        "./infra/services/__init__.py",
        "./functions/__init__.py",
    ]


def test_it_should_create_the_files_with_public_docs():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--bucket",
            "bucket",
            "--public-docs",
        ],
    )
    files = list_files(".")

    assert files == [
        "./generate_docs.py",
        "./conftest.py",
        "./pytest.ini",
        "./requirements.txt",
        "./.pre-commit-config.yaml",
        "./cdk.context.json",
        "./cdk.json",
        "./__init__.py",
        "./.coveragerc",
        "./source.bat",
        "./validate_docs.py",
        "./swagger_yml_to_ui.py",
        "./.gitignore",
        "./app.py",
        "./validate_integration_tests.py",
        "./infra/__init__.py",
        "./infra/stacks/staging_stack.py",
        "./infra/stacks/lambda_stack.py",
        "./infra/stacks/__init__.py",
        "./infra/stacks/prod_stack.py",
        "./infra/stacks/dev_stack.py",
        "./infra/stages/__init__.py",
        "./infra/steps/__init__.py",
        "./infra/steps/code_build_step.py",
        "./infra/services/api_gateway.py",
        "./infra/services/aws_lambda.py",
        "./infra/services/__init__.py",
        "./functions/__init__.py",
        "./functions/docs/config.py",
        "./functions/docs/__init__.py",
    ]


def test_it_should_update_lambda_stack_with_no_docs():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--no-docs",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack == [
        "from aws_cdk import Stack",
        "from constructs import Construct",
        "from infra.services import Services",
        "",
        "",
        "class LambdaStack(Stack):",
        "    def __init__(",
        "        self,",
        "        scope: Construct,",
        "        stage,",
        "        arns,",
        "        **kwargs,",
        "    ) -> None:",
        "",
        '        name = scope.node.try_get_context("name")',
        '        super().__init__(scope, f"{name}-CDK", **kwargs)',
        "",
        "        self.services = Services(self, stage, arns)",
    ]


def test_it_should_update_lambda_stack_with_public_docs():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--public-docs",
            "--bucket",
            "bucket",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack == [
        "from functions.docs.config import DocsConfig",
        "from aws_cdk import Stack",
        "from constructs import Construct",
        "from infra.services import Services",
        "",
        "",
        "class LambdaStack(Stack):",
        "    def __init__(",
        "        self,",
        "        scope: Construct,",
        "        stage,",
        "        arns,",
        "        **kwargs,",
        "    ) -> None:",
        "",
        '        name = scope.node.try_get_context("name")',
        '        super().__init__(scope, f"{name}-CDK", **kwargs)',
        "",
        "        self.services = Services(self, stage, arns)",
        "",
        "        # Docs",
        "        DocsConfig(self.services)",
    ]


def test_it_should_always_update_lambda_stack_with_private_docs():
    runner.invoke(
        project,
        [
            "project_name",
            "--repo-owner",
            "owner",
            "--repo-name",
            "repo",
            "--bucket",
            "bucket",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack == [
        "from functions.docs.config import DocsConfig",
        "from functions.authorizers.docs_authorizer.config import "
        "DocsAuthorizerConfig",
        "from aws_cdk import Stack",
        "from constructs import Construct",
        "from infra.services import Services",
        "",
        "",
        "class LambdaStack(Stack):",
        "    def __init__(",
        "        self,",
        "        scope: Construct,",
        "        stage,",
        "        arns,",
        "        **kwargs,",
        "    ) -> None:",
        "",
        '        name = scope.node.try_get_context("name")',
        '        super().__init__(scope, f"{name}-CDK", **kwargs)',
        "",
        "        self.services = Services(self, stage, arns)",
        "",
        "        # Authorizers",
        "        DocsAuthorizerConfig(self.services)",
        "",
        "        # Docs",
        "        DocsConfig(self.services)",
    ]
