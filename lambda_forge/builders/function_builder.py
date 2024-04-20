from lambda_forge.builders.file_service import FileService


class FunctionBuilder(FileService):
    @staticmethod
    def a_function(function_name, description=""):
        return FunctionBuilder(function_name, description)

    def __init__(self, function_name, description):
        self.function_name = function_name
        self.description = description
        self.endpoint = None
        self.integration = None
        self.main = None
        self.unit = None

    def with_endpoint(self, endpoint):
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        self.endpoint = endpoint
        return self

    def with_config(self, belongs):
        self.belongs = belongs
        self.pascal_name = "".join(word.capitalize() for word in self.function_name.split("_"))
        directory = f'directory="{self.function_name}"' if belongs else ""
        self.config = f"""from infra.services import Services

class {self.pascal_name}Config:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="{self.pascal_name}",
            path="./functions/{belongs or self.function_name}",
            description="{self.description}",
            {directory}
        )
"""
        return self

    def with_api(self, http_method, public):
        self.http_method = http_method
        if public:
            self.config += f"""
        services.api_gateway.create_endpoint("{http_method}", "/{self.endpoint}", function, public=True)

            """
        else:
            self.config += f"""
        services.api_gateway.create_endpoint("{http_method}", "/{self.endpoint}", function)

            """
        return self

    def with_websocket(self):

        self.config += f"""
        services.websockets.create_route("", function)

            """
        return self

    def with_integration(self, http_method):
        self.integration = f"""import pytest
import requests
from lambda_forge.constants import BASE_URL

@pytest.mark.integration(method="{http_method}", endpoint="/{self.endpoint}")
def test_{self.function_name}_status_code_is_200():

    response = requests.{http_method.lower()}(url=f"{{BASE_URL}}/{self.endpoint}")

    assert response.status_code == 200 
"""
        return self

    def with_main(self):
        docs = "import json\n"
        if self.endpoint:
            docs += "from dataclasses import dataclass\n"
            if "{" in self.endpoint and "}" in self.endpoint:
                docs += """
@dataclass
class Path:
    pass
"""
            docs += """
@dataclass
class Input:
    pass

@dataclass
class Output:
    message: str
"""
        self.main = f"""{docs}

def lambda_handler(event, context):

    return {{
        "statusCode": 200,
        "body": json.dumps({{"message": "Hello World!"}})
    }}
"""
        return self

    def with_unit(self):
        self.unit = """import json
from .main import lambda_handler

def test_lambda_handler():

    response = lambda_handler(None, None)

    assert response["body"] == json.dumps({"message": "Hello World!"})
"""
        return self

    def with_lambda_stack(self, docs=False):
        self.lambda_stack = self.read_lines("infra/stacks/lambda_stack.py")

        folder = f"functions.{self.belongs}.{self.function_name}" if self.belongs else f"functions.{self.function_name}"

        if folder in self.lambda_stack:
            return self

        self.lambda_stack.insert(0, f"from {folder}.config import {self.pascal_name}Config\n")

        directory = self.belongs or self.function_name
        comment = "".join(word.capitalize() for word in directory.split("_"))
        if docs:
            class_instance = f"        {self.pascal_name}Config(scope, self.services)\n"
        else:
            class_instance = f"        {self.pascal_name}Config(self.services)\n"
        try:
            comment_index = self.lambda_stack.index(f"        # {comment}\n")
            self.lambda_stack.insert(comment_index + 1, class_instance)
        except:
            self.lambda_stack.append(f"\n")
            self.lambda_stack.append(f"        # {comment}\n")
            self.lambda_stack.append(class_instance)

        return self

    def build(self):
        if self.belongs:
            folder_path = self.join("functions", self.belongs, self.function_name)
            self.make_dir(folder_path)
            self.make_file(folder_path, "__init__.py")
        else:
            folder_path = self.join("functions", self.function_name)
            self.make_dir(folder_path)
            self.make_file(folder_path, "__init__.py")

        self.make_file(folder_path, "config.py", self.config)
        if self.main:
            self.make_file(folder_path, "main.py", self.main)
        if self.unit:
            self.make_file(folder_path, "unit.py", self.unit)
        if self.integration:
            self.make_file(folder_path, "integration.py", self.integration)
        self.write_lines("infra/stacks/lambda_stack.py", self.lambda_stack)
