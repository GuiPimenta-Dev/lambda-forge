import dataclasses
import importlib
import json
import re


def get_endpoints(functions, api_endpoints):
    return [
        {
            "file_path": function["file_path"],
            "name": function_name,
            "description": function["description"],
            "endpoint": api_endpoints[function_name]["endpoint"],
            "method": api_endpoints[function_name]["method"],
        }
        for function in functions
        if (function_name := function["name"]) in api_endpoints
    ]


def extract_path_parameters(endpoint):
    return re.findall(r"\{(.*?)\}", endpoint)


def default_module_loader(file_path):
    return importlib.import_module(transform_file_path(file_path))


def transform_file_path(file_path):
    if file_path.startswith("./"):
        file_path = file_path[2:]

    # Replace '/' with '.' and remove the last part if it contains '.'
    parts = file_path.split("/")
    if "." in parts[-1]:
        parts[-1] = parts[-1].split(".")[0]

    return ".".join(parts)


def validate_dataclass(file_path, attribute_name, attribute):
    if not dataclasses.is_dataclass(attribute):
        raise Exception(
            f"{attribute_name} is not a dataclass on {transform_file_path(file_path)}"
        )


def validate_paths(endpoint, function_file):
    if "{" not in endpoint["endpoint"] and "}" not in endpoint["endpoint"]:
        return
    path = getattr(function_file, "Path", None)
    if path is None:
        raise Exception(
            f"Path is missing on {transform_file_path(endpoint['file_path'])}"
        )

    validate_dataclass(endpoint["file_path"], "Path", path)

    path_parameters = extract_path_parameters(endpoint["endpoint"])
    typed_args = list(path.__dataclass_fields__.keys())
    for parameter in path_parameters:
        if parameter not in typed_args:
            raise Exception(
                f"Path parameter {parameter} is missing in Path on {transform_file_path(endpoint['file_path'])}"
            )


def validate_docs(endpoints, loader=default_module_loader):
    for endpoint in endpoints:
        function_file = loader(endpoint["file_path"])

        validate_paths(endpoint, function_file)

        for attr_name in ["Input", "Output"]:
            attribute = getattr(function_file, attr_name, None)
            if attribute is None:
                raise Exception(
                    f"{attr_name} is missing on {transform_file_path(endpoint['file_path'])}"
                )
            validate_dataclass(endpoint["file_path"], attr_name, attribute)


if __name__ == "__main__":
    with open("cdk.json", "r") as json_file:
        context = json.load(json_file)["context"]
        arns = context["dev"]["arns"]

    import aws_cdk as cdk
    from infra.stacks.lambda_stack import LambdaStack

    app = cdk.App()
    services = LambdaStack(app, "Dev", arns).services
    functions = services.aws_lambda.functions
    api_endpoints = services.api_gateway.endpoints
    endpoints = get_endpoints(functions, api_endpoints)
    validate_docs(endpoints)
