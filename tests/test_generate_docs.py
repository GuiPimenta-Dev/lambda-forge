import pytest

from lambda_forge.files.generate_docs import generate_docs
from lambda_forge.files.ref_generate_docs import generate_docs as ref_generate_docs
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


def test_it_should_generate_the_docs():
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

    spec = generate_docs(functions, api_endpoints, "name")

    assert spec == {
        "components": {
            "schemas": {
                "FunctionNameInput": {
                    "properties": {
                        "a_boolean": {"type": "boolean"},
                        "a_list": {"items": {"type": "string"}, "type": "array"},
                        "a_literal": {"enum": ["a", "b", "c"], "type": "string"},
                        "a_string": {"type": "string"},
                        "an_int": {"type": "integer"},
                        "an_object": {
                            "properties": {
                                "a_string": {"type": "string"},
                                "an_int": {"type": "integer"},
                            },
                            "required": ["a_string", "an_int"],
                            "type": "object",
                        },
                        "an_optional": {"type": "string"},
                    },
                    "required": [
                        "a_string",
                        "an_int",
                        "a_boolean",
                        "a_list",
                        "an_object",
                        "a_literal",
                    ],
                },
                "FunctionNameOutput": {
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                },
            }
        },
        "info": {"description": "", "title": "Name Docs", "version": "1.0.0"},
        "openapi": "3.0.3",
        "paths": {
            "/function_name": {
                "get": {
                    "operationId": "FunctionName",
                    "parameters": [
                        {
                            "in": "query",
                            "name": "a_string",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "in": "query",
                            "name": "an_int",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "query",
                            "name": "a_boolean",
                            "required": True,
                            "schema": {"type": "boolean"},
                        },
                        {
                            "in": "query",
                            "name": "a_list",
                            "required": True,
                            "schema": {"items": {"type": "string"}, "type": "array"},
                        },
                        {
                            "in": "query",
                            "name": "an_object",
                            "required": True,
                            "schema": {"type": "object"},
                        },
                        {
                            "in": "query",
                            "name": "a_literal",
                            "required": True,
                            "schema": {"enum": ["a", "b", "c"], "type": "string"},
                        },
                        {
                            "in": "query",
                            "name": "an_optional",
                            "required": False,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/FunctionNameOutput"
                                    }
                                }
                            },
                            "description": "Successful " "response",
                        }
                    },
                    "summary": "description",
                    "tags": ["Function_name"],
                }
            }
        },
    }


def test_it_should_generate_the_refactored_docs():
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

    spec = ref_generate_docs(functions, api_endpoints, "name")

    assert spec == {
        "components": {
            "schemas": {
                "FunctionNameInput": {
                    "properties": {
                        "a_boolean": {"type": "boolean"},
                        "a_list": {"items": {"type": "string"}, "type": "array"},
                        "a_literal": {"enum": ["a", "b", "c"], "type": "string"},
                        "a_string": {"type": "string"},
                        "an_int": {"type": "integer"},
                        "an_object": {
                            "properties": {
                                "a_string": {"type": "string"},
                                "an_int": {"type": "integer"},
                            },
                            "required": ["a_string", "an_int"],
                            "type": "object",
                        },
                        "an_optional": {"type": "string"},
                    },
                    "required": [
                        "a_string",
                        "an_int",
                        "a_boolean",
                        "a_list",
                        "an_object",
                        "a_literal",
                    ],
                },
                "FunctionNameOutput": {
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                },
            }
        },
        "info": {"description": "", "title": "Name Docs", "version": "1.0.0"},
        "openapi": "3.0.3",
        "paths": {
            "/function_name": {
                "get": {
                    "operationId": "FunctionName",
                    "parameters": [
                        {
                            "in": "query",
                            "name": "a_string",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "in": "query",
                            "name": "an_int",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "query",
                            "name": "a_boolean",
                            "required": True,
                            "schema": {"type": "boolean"},
                        },
                        {
                            "in": "query",
                            "name": "a_list",
                            "required": True,
                            "schema": {"items": {"type": "string"}, "type": "array"},
                        },
                        {
                            "in": "query",
                            "name": "an_object",
                            "required": True,
                            "schema": {"type": "object"},
                        },
                        {
                            "in": "query",
                            "name": "a_literal",
                            "required": True,
                            "schema": {"enum": ["a", "b", "c"], "type": "string"},
                        },
                        {
                            "in": "query",
                            "name": "an_optional",
                            "required": False,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/FunctionNameOutput"
                                    }
                                }
                            },
                            "description": "Successful " "response",
                        }
                    },
                    "summary": "description",
                    "tags": ["Function_name"],
                }
            }
        },
    }
