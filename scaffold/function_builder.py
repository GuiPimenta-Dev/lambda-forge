import os

from scaffold.file_service import FileService



class FunctionBuilder(FileService):
    @staticmethod
    def a_file(function_name, description):
        return FunctionBuilder(function_name, description)
    
    def __init__(self, function_name, description):
        self.function_name = function_name
        self.description = description
        self.endpoint = None
        self.integration = None
        

    def with_endpoint(self, endpoint):
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        self.endpoint = endpoint
        return self

    def with_config(self, belongs):
        self.belongs = belongs
        self.pascal_name = "".join(word.capitalize() for word in self.function_name.split("_"))
        directory = f"directory=\"{self.function_name}\"" if belongs else ""
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
    
    def with_api(self, http_method):
        self.http_method = http_method
        self.config += f"""
        services.api_gateway.create_endpoint("{http_method}", "/{self.endpoint}", function)

        """        
        return self
    
    def with_integration(self, http_method):
        self.integration = f"""import pytest
import requests

@pytest.mark.integration(method="{http_method}", endpoint="/{self.endpoint}")
def test_{self.function_name}_status_code_is_200():

    response = requests.{http_method.lower()}(url="")

    assert response.status_code == 200 
"""
        return self
    
    def with_main(self):
        docs = "import json\n"
        if self.endpoint:
            if "{" in self.endpoint and "}" in self.endpoint:
                docs += f"""
# @dataclass
class Path:
    pass
"""         
            docs += """
# @dataclass
class Input:
    pass


# @dataclass
class Output:
    pass
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
        self.unit =  """import json
from .main import lambda_handler

def test_lambda_handler():

    response = lambda_handler(None, None)

    assert response["body"] == json.dumps({"message": "Hello World!"})
"""
        return self
    
    def with_lambda_stack(self):
        with open("infra/stacks/lambda_stack.py", "r") as f:
            lines = f.readlines()

            folder = f"functions.{self.belongs}.{self.function_name}" if self.belongs else f"functions.{self.function_name}"

            lines.insert(0, f"from {folder}.config import {self.pascal_name}\n")

            directory = self.belongs or self.function_name
            comment = "".join(word.capitalize() for word in directory.split("_"))

            try:
                comment_index = lines.index(f"        # {comment}\n")
                lines.insert(comment_index + 1, f"        {self.pascal_name}(self.services)\n")
            except:
                lines.append(f"\n")
                lines.append(f"        # {comment}\n")
                lines.append(f"        {self.pascal_name}(self.services)\n")
        
        self.lambda_stack = lines
        return self

    def build(self):
        if self.belongs:
           folder_path = self.join("functions", self.belongs, self.function_name)
           self.make_dir(folder_path)
           self.make_dir(f"functions/{self.belongs}/utils")
           self.make_file(folder_path, "__init__.py")
           self.make_file(f"functions/{self.belongs}/utils", "__init__.py")
        else:
            folder_path = os.path.join("functions", self.function_name)
            self.make_dir(folder_path)
            self.make_file(folder_path, "__init__.py")

        self.make_file(folder_path, "config.py", self.config)
        self.make_file(folder_path, "main.py", self.main)
        self.make_file(folder_path, "unit.py", self.unit)
        self.write_lines("infra/stacks/lambda_stack.py", self.lambda_stack)
        if self.integration:
            self.make_file(folder_path, "integration.py", self.integration)
        

        

    