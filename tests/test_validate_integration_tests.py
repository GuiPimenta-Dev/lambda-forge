import pytest
from lambda_forge.validate_integration_tests import validate_tests


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

    assert str(exc_info.value) == "Endpoint /function_name with method GET should have at least 1 integration test."
