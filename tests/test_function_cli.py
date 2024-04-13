import pytest
from click.testing import CliRunner
from pprint import pprint

from lambda_forge.cli import project, function
from tests.conftest import read_file_lines, list_files_related_to, list_files

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


def test_it_should_raise_an_error_if_no_api_is_false_and_not_http_method_and_authorizer_is_false():

    result = runner.invoke(function, ["function_name", "--description", "description"])
    assert (
        result.output
        == "Usage: function [OPTIONS] NAME\nTry 'function --help' for help.\n\nError: You must provide a method for the API Gateway endpoint or use the flag --no-api\n"
    )


def test_it_should_create_the_correct_folders_for_when_creating_a_function_with_no_api():

    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--no-api",
        ],
    )

    files = list_files_related_to("functions/function_name")
    assert files == [
        "./functions/function_name/config.py",
        "./functions/function_name/__init__.py",
        "./functions/function_name/unit.py",
        "./functions/function_name/main.py",
    ]


def test_it_should_configure_the_config_file_correctly_for_a_no_api_function():

    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--no-api",
        ],
    )

    config = read_file_lines("functions/function_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class FunctionNameConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="FunctionName",',
        '            path="./functions/function_name",',
        '            description="description",',
        "            ",
        "        )",
    ]


def test_it_should_configure_the_config_file_correctly_for_a_public_function():

    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--method",
            "GET",
            "--public",
        ],
    )

    config = read_file_lines("functions/function_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class FunctionNameConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="FunctionName",',
        '            path="./functions/function_name",',
        '            description="description",',
        "            ",
        "        )",
        "",
        '        services.api_gateway.create_endpoint("GET", "/function_name", ' "function, public=True)",
        "",
        "            ",
    ]


def test_it_should_configure_the_config_file_correctly_for_a_belongs_and_no_api_function():

    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--no-api",
            "--belongs",
            "belongs",
        ],
    )

    config = read_file_lines("functions/belongs/function_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class FunctionNameConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="FunctionName",',
        '            path="./functions/belongs",',
        '            description="description",',
        '            directory="function_name"',
        "        )",
    ]


def test_it_should_configure_the_config_file_correctly_for_a_belongs_and_with_api_function():
    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--belongs",
            "belongs",
            "--method",
            "GET",
        ],
    )

    config = read_file_lines("functions/belongs/function_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class FunctionNameConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="FunctionName",',
        '            path="./functions/belongs",',
        '            description="description",',
        '            directory="function_name"',
        "        )",
        "",
        '        services.api_gateway.create_endpoint("GET", "/belongs", function)',
        "",
        "            ",
    ]


def test_it_should_configure_the_config_file_correctly_for_a_api_function():
    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--method",
            "GET",
        ],
    )

    config = read_file_lines("functions/function_name/config.py")
    assert config == [
        "from infra.services import Services",
        "",
        "class FunctionNameConfig:",
        "    def __init__(self, services: Services) -> None:",
        "",
        "        function = services.aws_lambda.create_function(",
        '            name="FunctionName",',
        '            path="./functions/function_name",',
        '            description="description",',
        "            ",
        "        )",
        "",
        '        services.api_gateway.create_endpoint("GET", "/function_name", ' "function)",
        "",
        "            ",
    ]


def test_it_should_create_the_correct_folders_for_when_creating_a_function_with_api_and_belongs():

    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--method",
            "GET",
            "--belongs",
            "belongs",
        ],
    )

    files = list_files_related_to("/functions/belongs")
    assert files == [
        "./functions/belongs/function_name/config.py",
        "./functions/belongs/function_name/__init__.py",
        "./functions/belongs/function_name/integration.py",
        "./functions/belongs/function_name/unit.py",
        "./functions/belongs/function_name/main.py",
        "./functions/belongs/utils/__init__.py",
    ]


def test_it_should_create_the_correct_folders_for_when_creating_a_function_with_api_and_not_belongs():

    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--method",
            "GET",
        ],
    )

    files = list_files_related_to("/functions/function_name")
    assert files == [
        "./functions/function_name/config.py",
        "./functions/function_name/__init__.py",
        "./functions/function_name/integration.py",
        "./functions/function_name/unit.py",
        "./functions/function_name/main.py",
    ]


def test_it_should_update_lambda_stack_with_no_belongs():
    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--method",
            "GET",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack == [
        "from functions.function_name.config import FunctionNameConfig",
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
        "        DocsAuthorizerConfig(self.services)",
        "",
        "        # FunctionName",
        "        FunctionNameConfig(self.services)",
    ]


def test_it_should_update_lambda_stack_with_belongs():
    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--method",
            "GET",
            "--belongs",
            "belongs",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack == [
        "from functions.belongs.function_name.config import FunctionNameConfig",
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
        "        DocsAuthorizerConfig(self.services)",
        "",
        "        # Belongs",
        "        FunctionNameConfig(self.services)",
    ]


def test_it_should_add_the_function_at_the_end_of_lambda_stack():
    runner.invoke(
        function,
        [
            "function_name",
            "--description",
            "description",
            "--method",
            "GET",
        ],
    )

    lambda_stack = read_file_lines("infra/stacks/lambda_stack.py")
    assert lambda_stack[-2] == "        # FunctionName"
    assert lambda_stack[-1] == "        FunctionNameConfig(self.services)"
