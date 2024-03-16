import time
import pytest
from click.testing import CliRunner
from pprint import pprint

from lambda_forge.files.validate_docs import get_endpoints, validate_docs
from lambda_forge.main import project, function

runner = CliRunner()


def extract_file_path(file_path):
    return file_path.split(".lambda_handler")[0] + ".py"


def write_to_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)


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


def test_it_should_not_throw_an_error_if_docs_are_set():

    functions = [
        {
            "file_path": "./functions/authorizers/docs_authorizer/main.lambda_handler",
            "name": "DocsAuthorizer",
            "description": "Function used to authorize the docs endpoints",
        },
        {
            "file_path": "./functions/function_name/main.lambda_handler",
            "name": "FunctionName",
            "description": "description",
        },
    ]
    api_endpoints = {"FunctionName": {"method": "GET", "endpoint": "/function_name"}}

    endpoints = get_endpoints(functions, api_endpoints)
    try:
        validate_docs(endpoints)
    except:
        pytest.fail("It should not throw an error")


@pytest.mark.skip
def test_it_should_throw_an_error_if_input_is_not_a_dataclass():
    file_path = "./functions/function_name/main.py"
    content = """import json
from dataclasses import dataclass

class Input:
    pass

@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello World!"})
    }
"""
    write_to_file(file_path, content)

    functions = [
        {
            "file_path": "./functions/authorizers/docs_authorizer/main.lambda_handler",
            "name": "DocsAuthorizer",
            "description": "Function used to authorize the docs endpoints",
        },
        {
            "file_path": "./functions/function_name/main.lambda_handler",
            "name": "FunctionName",
            "description": "description",
        },
    ]
    api_endpoints = {"FunctionName": {"method": "GET", "endpoint": "/function_name"}}

    endpoints = get_endpoints(functions, api_endpoints)

    with pytest.raises(Exception) as exc_info:
        validate_docs(endpoints)

    assert (
        str(exc_info.value)
        == "Input is not a dataclass on functions/function_name/main"
    )
