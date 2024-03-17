import pytest
from lambda_forge.files.validate_integration_tests import get_endpoints, validate_tests


def test_it_correctly_should_retrieve_the_endpoints():

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

    assert endpoints == [{"method": "GET", "endpoint": "/function_name"}]


def test_it_should_not_raise_an_error_if_all_endpoints_are_tested():
    tested_endpoints = [{"method": "GET", "endpoint": "/function_name"}]
    endpoints = [{"method": "GET", "endpoint": "/function_name"}]

    try:
        validate_tests(endpoints, tested_endpoints)
    except:
        pytest.fail("It should not throw an error")


def test_it_should_raise_an_error_if_not_all_endpoints_are_tested():

    tested_endpoints = []
    endpoints = [{"method": "GET", "endpoint": "/function_name"}]

    with pytest.raises(Exception) as exc_info:
        validate_tests(endpoints, tested_endpoints)

    assert (
        str(exc_info.value)
        == "Endpoint /function_name with method GET should have at least 1 integration test."
    )
