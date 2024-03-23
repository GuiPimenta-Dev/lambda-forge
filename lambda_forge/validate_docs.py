import dataclasses
import importlib
import json
import re


def extract_path_parameters(endpoint):
    return re.findall(r"\{(.*?)\}", endpoint)


def default_module_loader(path):
    return importlib.import_module(transform_file_path(f"{path}/main.lambda_handler"))


def transform_file_path(path):
    if path.startswith("./"):
        path = path[2:]

    # Replace '/' with '.' and remove the last part if it contains '.'
    parts = path.split("/")
    if "." in parts[-1]:
        parts[-1] = parts[-1].split(".")[0]

    return ".".join(parts)


def validate_dataclass(path, attribute_name, attribute):
    if not dataclasses.is_dataclass(attribute):
        raise Exception(
            f"{attribute_name} is not a dataclass on {transform_file_path(path)}.main"
        )


def validate_paths(endpoint, function_file):
    if "{" not in endpoint["endpoint"] and "}" not in endpoint["endpoint"]:
        return
    path = getattr(function_file, "Path", None)
    if path is None:
        raise Exception(
            f"Path is missing on {transform_file_path(endpoint['path'])}.main"
        )

    validate_dataclass(endpoint["path"], "Path", path)

    path_parameters = extract_path_parameters(endpoint["endpoint"])
    typed_args = list(path.__dataclass_fields__.keys())
    for parameter in path_parameters:
        if parameter not in typed_args:
            raise Exception(
                f"Path parameter {parameter} is missing in Path on {transform_file_path(endpoint['path'])}.main"
            )


def validate_docs(endpoints, loader=default_module_loader):
    for endpoint in endpoints:
        function_file = loader(endpoint["path"])

        validate_paths(endpoint, function_file)

        for attr_name in ["Input", "Output"]:
            attribute = getattr(function_file, attr_name, None)
            if attribute is None:
                raise Exception(
                    f"{attr_name} is missing on {transform_file_path(endpoint['path'])}.main"
                )
            validate_dataclass(endpoint["path"], attr_name, attribute)


if __name__ == "__main__":
    with open("cdk.json", "r") as json_file:
        context = json.load(json_file)["context"]
        functions = context["functions"]
    endpoints = [endpoint for endpoint in functions if "method" in endpoint]
    validate_docs(endpoints)
