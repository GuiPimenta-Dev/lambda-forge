import random
import string
from lambda_forge.file_service import FileService


class FunctionBuilder(FileService):
    @staticmethod
    def a_function(function_name, description=""):
        return FunctionBuilder(function_name, description)

    def __init__(self, function_name, description):
        self.function_name = function_name
        self.description = description
        self.endpoint = None
        self.integration = None
        self.authorizer = False
        self.main = None
        self.unit = None

    def with_endpoint(self, endpoint):
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        self.endpoint = endpoint
        return self

    def with_custom_config(self, config, belongs=None):
        self.config = config
        self.belongs = belongs
        self.pascal_name = "".join(
            word.capitalize() for word in self.function_name.split("_")
        )
        return self

    def with_config(self, belongs):
        self.belongs = belongs
        self.pascal_name = "".join(
            word.capitalize() for word in self.function_name.split("_")
        )
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

    def with_authorizer_unit(self):
        self.unit = f"""from .main import lambda_handler

def test_authorizer_should_pass_with_correct_secret():

    secret = "{self.secret}"
    event = {{
        "headers": {{
            "secret": secret
        }}
    }}
    response = lambda_handler(event, None)

    assert response == {{
        "policyDocument": {{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Action": "execute-api:Invoke",
                    "Effect": "allow",
                    "Resource": "*"
                }}
            ],
        }},
    }}

def test_authorizer_should_fail_with_invalid_secret():

    secret = "INVALID-SECRET"
    event = {{
        "headers": {{
            "secret": secret
        }}
    }}
    response = lambda_handler(event, None)

    assert response == {{
        "policyDocument": {{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Action": "execute-api:Invoke",
                    "Effect": "deny",
                    "Resource": "*"
                }}
            ],
        }},
    }}
"""
        return self

    def with_authorizer(self, name=None, update_config=True):
        self.authorizer = True
        self.secret = "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=52))

        self.main = f"""
def lambda_handler(event, context):

    # ATTENTION: The example provided below is strictly for demonstration purposes and should NOT be deployed in a production environment.
    # It's crucial to develop and integrate your own robust authorization mechanism tailored to your application's security requirements.
    # To utilize the example authorizer as a temporary placeholder, ensure to include the following header in your requests:

    # Header:
    # secret: {self.secret}

    # Remember, security is paramount. This placeholder serves as a guide to help you understand the kind of information your custom authorizer should authenticate. 
    # Please replace it with your secure, proprietary logic before going live. Happy coding!

    secret = event["headers"].get("secret")

    SECRET = "{self.secret}"
    effect = "allow" if secret == SECRET else "deny"

    policy = {{
        "policyDocument": {{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": "*"
                }}
            ],
        }},
    }}
    return policy
"""
        if update_config:
            if name:
                self.config += f"""
            services.api_gateway.create_authorizer(function, name="{name}")
            """

            else:
                self.config += """        
        services.api_gateway.create_authorizer(function)
            """

        return self

    def with_lambda_stack(self):
        self.lambda_stack = self.read_lines("infra/stacks/lambda_stack.py")

        folder = (
            f"functions.{self.belongs}.{self.function_name}"
            if self.belongs
            else f"functions.{self.function_name}"
        )

        self.lambda_stack.insert(
            0, f"from {folder}.config import {self.pascal_name}Config\n"
        )

        directory = self.belongs or self.function_name
        comment = "".join(word.capitalize() for word in directory.split("_"))

        try:
            comment_index = self.lambda_stack.index(f"        # {comment}\n")
            self.lambda_stack.insert(
                comment_index + 1, f"        {self.pascal_name}Config(self.services)\n"
            )
        except:
            if self.authorizer is False:
                self.lambda_stack.append(f"\n")
                self.lambda_stack.append(f"        # {comment}\n")
                self.lambda_stack.append(
                    f"        {self.pascal_name}Config(self.services)\n"
                )
            else:
                services_index = next(
                    (
                        i
                        for i, line in enumerate(self.lambda_stack)
                        if "Services(self" in line
                    ),
                    -1,
                )
                self.lambda_stack.insert(services_index + 1, f"\n")
                self.lambda_stack.insert(services_index + 2, f"        # {comment}\n")
                self.lambda_stack.insert(
                    services_index + 3,
                    f"        {self.pascal_name}Config(self.services)\n",
                )

        return self

    def build(self):
        if self.belongs:
            folder_path = self.join("functions", self.belongs, self.function_name)
            self.make_dir(folder_path)
            self.make_dir(f"functions/{self.belongs}/utils")
            self.make_file(folder_path, "__init__.py")
            self.make_file(f"functions/{self.belongs}/utils", "__init__.py")
        else:
            folder_path = self.join("functions", self.function_name)
            self.make_dir(folder_path)
            self.make_file(folder_path, "__init__.py")

        self.make_file(folder_path, "config.py", self.config)
        if self.main:
            self.make_file(folder_path, "main.py", self.main)
        if self.unit:
            self.make_file(folder_path, "unit.py", self.unit)
        self.write_lines("infra/stacks/lambda_stack.py", self.lambda_stack)
        if self.integration:
            self.make_file(folder_path, "integration.py", self.integration)
