import pytest
from click.testing import CliRunner
from pprint import pprint

from lambda_forge.main import project, authorizer
from tests.conftest import read_file_lines, list_files_related_to

runner = CliRunner()


@pytest.fixture(scope="function", autouse=True)
def start_project():
    runner = CliRunner()
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


def test_it_should_create_the_correct_folders_for_an_authorizer():

    runner.invoke(
        authorizer,
        [
            "authorizer_name",
            "--description",
            "description",
        ],
    )

    files = list_files_related_to("authorizers/authorizer_name")
    assert files == [
        "./functions/authorizers/authorizer_name/config.py",
        "./functions/authorizers/authorizer_name/__init__.py",
        "./functions/authorizers/authorizer_name/unit.py",
        "./functions/authorizers/authorizer_name/main.py",
    ]


def test_it_should_configure_the_config_file_correctly_for_a_non_default_authorizer():

    runner.invoke(
        authorizer,
        [
            "authorizer_name",
            "--description",
            "description",
        ],
    )

    config = read_file_lines("functions/authorizers/authorizer_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class AuthorizerNameConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="AuthorizerName",',
        '            path="./functions/authorizers",',
        '            description="description",',
        '            directory="authorizer_name"',
        "        )",
        "",
        "        services.api_gateway.create_authorizer(function, "
        'name="authorizer_name", default=False)',
    ]


def test_it_should_configure_the_config_file_correctly_for_a_default_authorizer():

    runner.invoke(
        authorizer,
        ["authorizer_name", "--description", "description", "--default"],
    )

    config = read_file_lines("functions/authorizers/authorizer_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class AuthorizerNameConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="AuthorizerName",',
        '            path="./functions/authorizers",',
        '            description="description",',
        '            directory="authorizer_name"',
        "        )",
        "",
        "        services.api_gateway.create_authorizer(function, "
        'name="authorizer_name", default=True)',
    ]


def test_it_should_update_lambda_stack_when_creating_an_authorizer():
    runner.invoke(
        authorizer,
        [
            "authorizer_name",
            "--description",
            "description",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack == [
        "from functions.authorizers.authorizer_name.config import "
        "AuthorizerNameConfig",
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
        "        AuthorizerNameConfig(self.services)",
        "        DocsAuthorizerConfig(self.services)",
        "",
        "        # Docs",
        "        DocsConfig(scope, self.services)",
    ]


def test_it_should_add_the_authorizer_at_the_beggining_of_lambda_stack():
    runner.invoke(
        authorizer,
        [
            "authorizer_name",
            "--description",
            "description",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack[23] == "        AuthorizerNameConfig(self.services)"
