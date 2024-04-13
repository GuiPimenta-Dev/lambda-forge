import pytest
from click.testing import CliRunner
from pprint import pprint

from lambda_forge.cli import project, authorizer
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
        "./authorizers/authorizer_name/config.py",
        "./authorizers/authorizer_name/__init__.py",
        "./authorizers/authorizer_name/unit.py",
        "./authorizers/authorizer_name/main.py",
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

    config = read_file_lines("authorizers/authorizer_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class AuthorizerNameAuthorizerConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="AuthorizerNameAuthorizer",',
        '            path="./authorizers/authorizer_name",',
        '            description="description"',
        "        )",
        "",
        "        services.api_gateway.create_authorizer(function, " 'name="authorizer_name", default=False)',
    ]


def test_it_should_configure_the_config_file_correctly_for_a_default_authorizer():

    runner.invoke(
        authorizer,
        ["authorizer_name", "--description", "description", "--default"],
    )

    config = read_file_lines("authorizers/authorizer_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class AuthorizerNameAuthorizerConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="AuthorizerNameAuthorizer",',
        '            path="./authorizers/authorizer_name",',
        '            description="description"',
        "        )",
        "",
        "        services.api_gateway.create_authorizer(function, " 'name="authorizer_name", default=True)',
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
        "from authorizers.authorizer_name.config import " "AuthorizerNameAuthorizerConfig",
        "from authorizers.docs.config import DocsAuthorizerConfig",
        "from aws_cdk import Stack",
        "from constructs import Construct",
        "from infra.services import Services",
        "from lambda_forge import release",
        "",
        "",
        "@release",
        "class LambdaStack(Stack):",
        "    def __init__(self, scope: Construct, context, **kwargs) -> None:",
        "",
        '        super().__init__(scope, f"{context.name}-Lambda-Stack", **kwargs)',
        "",
        "        self.services = Services(self, context)",
        "",
        "        # Authorizers",
        "        AuthorizerNameAuthorizerConfig(self.services)",
        "        DocsAuthorizerConfig(self.services)",
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
    assert lambda_stack[17] == "        AuthorizerNameAuthorizerConfig(self.services)"


def test_it_should_not_add_the_authorizer_string_case_the_user_already_added_it():
    runner.invoke(
        authorizer,
        [
            "authorizer_name_authorizer",
            "--description",
            "description",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    config = read_file_lines("authorizers/authorizer_name_authorizer/config.py")
    assert lambda_stack[17] == "        AuthorizerNameAuthorizerConfig(self.services)"
    assert config == [
        "from infra.services import Services",
        "",
        "class AuthorizerNameAuthorizerConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="AuthorizerNameAuthorizer",',
        '            path="./authorizers/authorizer_name_authorizer",',
        '            description="description"',
        "        )",
        "",
        "        services.api_gateway.create_authorizer(function, " 'name="authorizer_name_authorizer", default=False)',
    ]
