import dataclasses
import importlib
import json
import re

import aws_cdk as cdk

from infra.stacks.lambda_stack import LambdaStack


def get_endpoints(functions, api_endpoints):
    endpoints = []
    for function in functions:
        function_name = function["name"]
        if function_name in api_endpoints:
            endpoint = api_endpoints[function_name]["endpoint"]
            method = api_endpoints[function_name]["method"]
            merged_obj = {
                "file_path": function["file_path"],
                "name": function_name,
                "description": function["description"],
                "endpoint": endpoint,
                "method": method,
            }
            endpoints.append(merged_obj)
    return endpoints


def extract_path_parameters(endpoint):
    pattern = r"\{(.*?)\}"
    matches = re.findall(pattern, endpoint)
    return matches


def default_module_loader(file_path):
    return importlib.import_module(file_path)


def validate_docs(endpoints, loader):
    paths = {endpoint["endpoint"]: {} for endpoint in endpoints}
    for endpoint in endpoints:
        print(endpoint)
        file_path = (
            endpoint["file_path"]
            .replace(".", "/")[2:]
            .replace("/", ".")
            .replace(".lambda_handler", "")
        )
        function_file = loader(file_path)

        if "{" in endpoint["endpoint"] and "}" in endpoint["endpoint"]:
            try:
                path = function_file.Path
            except AttributeError:
                raise Exception(f"Path is missing on {file_path.replace('.', '/')}")

            if not dataclasses.is_dataclass(path):
                raise Exception(
                    f"Path is not a dataclass on {file_path.replace('.', '/')}"
                )

            paths = extract_path_parameters(endpoint["endpoint"])
            typed_args = list(path.__dataclass_fields__.keys())
            for path in paths:
                if path not in typed_args:
                    raise Exception(
                        f"Path parameter {path} is missing in Path on {file_path.replace('.', '/')}"
                    )

        try:
            input_ = function_file.Input
        except AttributeError:
            raise Exception(f"Input is missing on {file_path.replace('.', '/')}")

        try:
            output = function_file.Output
        except AttributeError:
            raise Exception(f"Output is missing on {file_path.replace('.', '/')}")

        if not dataclasses.is_dataclass(input_):
            raise Exception(
                f"Input is not a dataclass on {file_path.replace('.', '/')}"
            )

        if not dataclasses.is_dataclass(output):
            raise Exception(
                f"Output is not a dataclass on {file_path.replace('.', '/')}"
            )


if __name__ == "__main__":
    with open("cdk.json", "r") as json_file:
        context = json.load(json_file)["context"]
        arns = context["dev"]["arns"]

    services = LambdaStack(cdk.App(), "Dev", arns).services
    functions = services.aws_lambda.functions
    api_endpoints = services.api_gateway.endpoints
    endpoints = get_endpoints(functions, api_endpoints)
    validate_docs(endpoints, default_module_loader)
