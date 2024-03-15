import importlib
import json
from copy import deepcopy

import aws_cdk as cdk
import yaml

from infra.stacks.lambda_stack import LambdaStack

with open("cdk.json", "r") as json_file:
    context = json.load(json_file)["context"]
    name = context["name"]
    arns = context["dev"]["arns"]

info = {
    "title": f"{name.title()} Docs",
    "description": "",
    "version": "1.0.0",
}


services = LambdaStack(
    cdk.App(),
    "Dev",
    arns,
).services

functions = services.aws_lambda.functions
api_endpoints = services.api_gateway.endpoints

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


schemas = []
paths = {endpoint["endpoint"]: {} for endpoint in endpoints}
for endpoint in endpoints:
    method = endpoint["method"].lower()
    tag = endpoint["endpoint"].split("/")[1].capitalize()
    repo_name = endpoint["name"]
    summary = endpoint["description"]
    file_path = (
        endpoint["file_path"]
        .replace(".", "/")[2:]
        .replace("/", ".")
        .replace(".lambda_handler", "")
    )
    endpoint = endpoint["endpoint"]
    paths[endpoint][method] = {
        "tags": [tag],
        "summary": summary,
        "operationId": repo_name,
    }

    function_file = importlib.import_module(file_path)
    _input = function_file.Input
    output = function_file.Output
    if "{" in endpoint and "}" in endpoint:
        _path = function_file.Path
        schemas.extend(
            (
                {"data": _input, "name": f"{repo_name}Input"},
                {"data": output, "name": f"{repo_name}Output"},
                {"data": _path, "name": f"{repo_name}Path"},
            )
        )
    else:
        schemas.extend(
            (
                {"data": _input, "name": f"{repo_name}Input"},
                {"data": output, "name": f"{repo_name}Output"},
            )
        )


def parse_schema(data):
    schemas = {}
    for item in data:
        dtclass = item["data"]
        name = item["name"]
        properties, required = parse_dtclass(dtclass)
        schemas[name] = (
            {"properties": properties, "required": required}
            if required
            else {"properties": properties}
        )
    return schemas


def parse_dtclass(dtclass):
    schemas = {}
    required = []
    for i, j in dtclass.__dataclass_fields__.items():
        type_ = str(j.type)
        swagger_type = None
        items = None
        properties = None
        enum = None
        if "List" in type_:
            swagger_type = "array"
            if "str" in type_:
                items = {"type": "string"}
            elif "int" in type_:
                items = {"type": "integer"}
            elif "float" in type_:
                items = {"type": "number"}
            elif "functions" in type_:
                properties, required_props = parse_dtclass(j.type.__args__[0])
                items = {
                    "type": "object",
                    "properties": properties,
                    "required": required_props,
                }
        elif "functions" in type_:
            swagger_type = "object"
            if "Optional" in type_:
                properties, required_props = parse_dtclass(j.type.__args__[0])
            else:
                properties, required_props = parse_dtclass(j.type)
        elif "Dict" in type_:
            swagger_type = "object"
        elif "str" in type_:
            swagger_type = "string"
        elif "int" in type_:
            swagger_type = "integer"
        elif "float" in type_:
            swagger_type = "number"
        elif "bool" in type_:
            swagger_type = "boolean"

        if "Optional" not in type_:
            required.append(i)

        if "Literal" in type_:
            data = (
                j.type.__args__[0].__args__ if "Optional" in type_ else j.type.__args__
            )
            enum = list(data)
            if isinstance(data[0], str):
                swagger_type = "string"
            elif isinstance(data[0], int):
                swagger_type = "integer"

        if items:
            schemas[i] = {"type": swagger_type, "items": items}
        elif properties:
            schemas[i] = (
                {
                    "type": swagger_type,
                    "properties": properties,
                    "required": required_props,
                }
                if required_props
                else {
                    "type": swagger_type,
                    "properties": properties,
                }
            )
        else:
            schemas[i] = {"type": swagger_type}

        if enum:
            schemas[i]["enum"] = enum

    return schemas, required


def parse_input_output(paths, schemas):
    for endpoint, path in paths.items():
        for method, data in path.items():
            responses = {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{data['operationId']}Output"
                            }
                        }
                    },
                }
            }
            input_name = f"{data['operationId']}Input"
            path_params = schemas.get(f"{data['operationId']}Path")
            path_list = []
            if path_params:
                path_list = parse_path_properties(path_params)
            if method == "get":
                parameters = parse_get_properties(schemas[input_name])
                paths[endpoint][method]["parameters"] = path_list + parameters

            else:
                paths[endpoint][method]["requestBody"] = parse_post_properties(
                    input_name
                )
                if path_params:
                    paths[endpoint][method]["parameters"] = path_list

            paths[endpoint][method]["responses"] = responses


def parse_get_properties(schema):
    parameters = []
    for _property in schema["properties"]:
        schema_type = {"type": schema["properties"][_property]["type"]}
        enum = schema["properties"][_property].get("enum")
        if enum:
            schema_type["enum"] = enum
        items = schema["properties"][_property].get("items")
        if items:
            schema_type["items"] = deepcopy(items)

        parameters.append(
            {
                "name": _property,
                "in": "query",
                "required": _property in schema["required"],
                "schema": schema_type,
            }
        )
    return parameters


def parse_post_properties(schema_name):
    return {
        "content": {
            "application/json": {
                "schema": {"$ref": f"#/components/schemas/{schema_name}"}
            }
        },
    }


def parse_path_properties(schema):
    parameters = []
    for _property in schema["properties"]:
        schema_type = {"type": schema["properties"][_property]["type"]}

        parameters.append(
            {
                "name": _property,
                "in": "path",
                "required": True,
                "schema": schema_type,
            }
        )
    return parameters


schemas = parse_schema(schemas)
parse_input_output(paths, schemas)


spec = {
    "openapi": "3.0.3",
    "info": info,
    "paths": paths,
    "components": {"schemas": schemas},
}
with open(r"docs.yaml", "w") as f:
    yaml.dump(spec, f, sort_keys=True)
