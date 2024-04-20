import importlib
import json
from copy import deepcopy
import yaml


def get_paths(endpoints):
    paths = {endpoint["endpoint"]: {} for endpoint in endpoints}
    for endpoint in endpoints:
        method = endpoint["method"].lower()
        tag = endpoint["endpoint"].split("/")[1].capitalize()
        repo_name = endpoint["name"]
        summary = endpoint["description"]
        endpoint = endpoint["endpoint"]
        paths[endpoint][method] = {
            "tags": [tag],
            "summary": summary,
            "operationId": repo_name,
        }
    return paths


def normalize_file_path(file_path):
    """
    Converts the file path from the endpoint format to the loader format.
    """
    # Strip leading './' if it exists
    if file_path.startswith("./"):
        file_path = file_path[2:]

    # Replace '/' with '.' and remove the last part if it contains '.'
    parts = file_path.split("/")
    if "." in parts[-1]:
        parts[-1] = parts[-1].split(".")[0]

    return ".".join(parts)


def get_schemas_from_endpoint(endpoint, loader):
    """
    Generates schema definitions for a given endpoint.
    """
    repo_name = endpoint["name"]
    file_path = normalize_file_path(endpoint["path"])
    function_module = loader(file_path)

    schemas = [
        {"data": function_module.Input, "name": f"{repo_name}Input"},
        {"data": function_module.Output, "name": f"{repo_name}Output"},
    ]

    # If endpoint has a dynamic path, add the Path schema.
    if "{" in endpoint["endpoint"] and "}" in endpoint["endpoint"]:
        schemas.append({"data": function_module.Path, "name": f"{repo_name}Path"})

    return schemas


def get_schema(endpoints, loader):
    """
    Generates a list of schema definitions for a collection of endpoints.
    """
    all_schemas = []
    for endpoint in endpoints:
        endpoint_schemas = get_schemas_from_endpoint(endpoint, loader)
        all_schemas.extend(endpoint_schemas)

    return all_schemas


def parse_schema(data):
    """
    Parses a list of data representing schemas and converts them into a structured dictionary.

    Each item in the input data is expected to have 'data' (the class definition)
    and 'name' (the schema name) as keys.
    """
    schemas = {}
    for item in data:
        # Extract class and name from the current item.
        dtclass = item["data"]
        schema_name = item["name"]

        # Parse the class to get its properties and required fields.
        properties, required_fields = parse_dtclass(dtclass)

        # Always include properties; conditionally include required fields if present.
        schema_info = {"properties": properties}
        if required_fields:
            schema_info["required"] = required_fields

        schemas[schema_name] = schema_info

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
            data = j.type.__args__[0].__args__ if "Optional" in type_ else j.type.__args__
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


def create_response_object(operation_id):
    """Creates a standardized response object for an operation."""
    return {
        "200": {
            "description": "Successful response",
            "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{operation_id}Output"}}},
        }
    }


def update_parameters_for_get_method(paths, endpoint, method, schemas, data, path_params):
    """Updates the parameters for GET requests."""
    operation_id = data["operationId"]
    input_name = f"{operation_id}Input"
    path_list = parse_path_properties(path_params) if path_params else []
    parameters = parse_get_properties(schemas[input_name])
    paths[endpoint][method]["parameters"] = path_list + parameters


def update_request_body_for_other_methods(paths, endpoint, method, data, path_params):
    """Updates the request body and parameters for non-GET requests."""
    operation_id = data["operationId"]
    input_name = f"{operation_id}Input"
    paths[endpoint][method]["requestBody"] = parse_post_properties(input_name)
    if path_params:
        path_list = parse_path_properties(path_params)
        paths[endpoint][method]["parameters"] = path_list


def parse_path(paths, schemas):
    """Parses and updates paths with appropriate parameters and responses."""
    for endpoint, path in paths.items():
        for method, data in path.items():
            operation_id = data["operationId"]
            path_params = schemas.get(f"{operation_id}Path")

            if method == "get":
                update_parameters_for_get_method(paths, endpoint, method, schemas, data, path_params)
            else:
                update_request_body_for_other_methods(paths, endpoint, method, data, path_params)

            paths[endpoint][method]["responses"] = create_response_object(operation_id)

    return paths


def build_parameter_schema(property_schema):
    """Builds the schema for a parameter based on its definition in the property schema."""
    schema_type = {"type": property_schema["type"]}
    if "enum" in property_schema:
        schema_type["enum"] = property_schema["enum"]
    if "items" in property_schema:
        schema_type["items"] = deepcopy(property_schema["items"])
    return schema_type


def create_parameter(name, schema, required):
    """Creates a parameter dictionary for a single property."""
    return {
        "name": name,
        "in": "query",
        "required": required,
        "schema": build_parameter_schema(schema),
    }


def parse_get_properties(schema):
    """Parses properties from a schema and builds query parameters for a GET request."""
    parameters = []
    properties = schema.get("properties", {})
    required_properties = schema.get("required", [])

    for _property, property_schema in properties.items():
        parameter = create_parameter(
            name=_property,
            schema=property_schema,
            required=_property in required_properties,
        )
        parameters.append(parameter)

    return parameters


def parse_post_properties(schema_name):
    return {
        "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}},
    }


def parse_path_properties(schema):
    """Parses properties from a schema and builds path parameters."""
    parameters = []
    properties = schema.get("properties", {})

    for name, schema in properties.items():
        parameter = {
            "name": name,
            "in": "path",
            "required": True,
            "schema": {"type": schema["type"]},
        }
        parameters.append(parameter)

    return parameters


def default_module_loader(file_path):
    file_path = f"{file_path}.main"
    return importlib.import_module(file_path)


def generate_docs(endpoints, name, loader=default_module_loader):

    info = {
        "title": f"{name.title()} Docs",
        "description": "",
        "version": "1.0.0",
    }

    paths = get_paths(endpoints)
    schema = get_schema(endpoints, loader)

    parsed_schema = parse_schema(schema)
    parsed_path = parse_path(paths, parsed_schema)

    spec = {
        "openapi": "3.0.3",
        "info": info,
        "paths": parsed_path,
        "components": {"schemas": parsed_schema},
    }
    return spec


if __name__ == "__main__":

    with open("cdk.json", "r") as json_file:
        context = json.load(json_file)["context"]
        name = context["name"]
        functions = context["functions"]

    endpoints = [endpoint for endpoint in functions if "method" in endpoint]

    spec = generate_docs(endpoints, name)
    with open(r"docs.yaml", "w") as f:
        yaml.dump(spec, f, sort_keys=True)
