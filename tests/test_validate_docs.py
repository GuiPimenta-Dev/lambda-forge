import pytest

from lambda_forge.files.validate_docs import get_endpoints
from dataclasses import dataclass



class NotDataclass:
    pass


@dataclass
class ADataClass:
    pass


class Mock:
    def __init__(self) -> None:
        self.Input = ADataClass()
        self.Output = ADataClass()



def module_loader(content):
    def loader(file_path):
        return content

    return loader


def test_it_should_retrieve_the_endpoints():

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

    assert endpoints == [
        {
            "file_path": "./functions/function_name/main.lambda_handler",
            "name": "FunctionName",
            "description": "description",
            "endpoint": "/function_name",
            "method": "GET",
        }
    ]


# def test_it_should_not_throw_an_error_if_docs_are_set():

#     functions = [
#         {
#             "file_path": "./functions/authorizers/docs_authorizer/main.lambda_handler",
#             "name": "DocsAuthorizer",
#             "description": "Function used to authorize the docs endpoints",
#         },
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#         },
#     ]
#     api_endpoints = {"FunctionName": {"method": "GET", "endpoint": "/function_name"}}

#     endpoints = get_endpoints(functions, api_endpoints)
#     try:
#         validate_docs(endpoints, module_loader(Mock()))
#     except:
#         pytest.fail("It should not throw an error")


# def test_it_should_throw_an_error_if_input_is_not_a_dataclass():

#     mock = Mock()
#     mock.Input = NotDataclass()

#     endpoints = [
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#             "endpoint": "/function_name",
#             "method": "GET",
#         }
#     ]

#     with pytest.raises(Exception) as exc_info:
#         validate_docs(endpoints, module_loader(mock))

#     assert (
#         str(exc_info.value)
#         == "Input is not a dataclass on functions/function_name/main"
#     )


# def test_it_should_throw_an_error_if_output_is_not_a_dataclass():

#     mock = Mock()
#     mock.Output = NotDataclass()

#     endpoints = [
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#             "endpoint": "/function_name",
#             "method": "GET",
#         }
#     ]

#     with pytest.raises(Exception) as exc_info:
#         validate_docs(endpoints, module_loader(mock))

#     assert (
#         str(exc_info.value)
#         == "Output is not a dataclass on functions/function_name/main"
#     )


# def test_it_should_throw_an_error_if_input_is_missing():

#     mock = Mock()
#     del mock.Input

#     endpoints = [
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#             "endpoint": "/function_name",
#             "method": "GET",
#         }
#     ]

#     with pytest.raises(Exception) as exc_info:
#         validate_docs(endpoints, module_loader(mock))

#     assert str(exc_info.value) == "Input is missing on functions/function_name/main"


# def test_it_should_throw_an_error_if_output_is_missing():

#     mock = Mock()
#     del mock.Output

#     endpoints = [
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#             "endpoint": "/function_name",
#             "method": "GET",
#         }
#     ]

#     with pytest.raises(Exception) as exc_info:
#         validate_docs(endpoints, module_loader(mock))

#     assert str(exc_info.value) == "Output is missing on functions/function_name/main"


# def test_it_should_throw_an_error_if_path_id_parameter_is_missing_case_the_endpoint_has_the_path():

#     mock = Mock()
#     mock.Path = ADataClass()

#     endpoints = [
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#             "endpoint": "/function_name/{id}",
#             "method": "GET",
#         }
#     ]

#     with pytest.raises(Exception) as exc_info:
#         validate_docs(endpoints, module_loader(mock))

#     assert (
#         str(exc_info.value)
#         == "Path parameter id is missing in Path on functions/function_name/main"
#     )


# def test_it_should_throw_an_error_if_path_class_is_missing_case_the_endpoint_has_the_path():

#     mock = Mock()

#     endpoints = [
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#             "endpoint": "/function_name/{id}",
#             "method": "GET",
#         }
#     ]

#     with pytest.raises(Exception) as exc_info:
#         validate_docs(endpoints, module_loader(mock))

#     assert str(exc_info.value) == "Path is missing on functions/function_name/main"


# def test_it_should_throw_an_error_if_path_class_is_not_a_dataclass_case_the_endpoint_has_the_path():

#     mock = Mock()
#     mock.Path = NotDataclass()

#     endpoints = [
#         {
#             "file_path": "./functions/function_name/main.lambda_handler",
#             "name": "FunctionName",
#             "description": "description",
#             "endpoint": "/function_name/{id}",
#             "method": "GET",
#         }
#     ]

#     with pytest.raises(Exception) as exc_info:
#         validate_docs(endpoints, module_loader(mock))

#     assert (
#         str(exc_info.value) == "Path is not a dataclass on functions/function_name/main"
#     )
