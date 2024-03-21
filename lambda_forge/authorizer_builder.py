import random
import string
from lambda_forge.file_service import FileService


class AuthorizerBuilder(FileService):
    @staticmethod
    def an_authorizer(authorizer_name, description, belongs):
        return AuthorizerBuilder(authorizer_name, description, belongs)

    def __init__(self, authorizer_name, description, belongs):
        self.authorizer_name = authorizer_name
        self.description = description
        self.belongs = belongs
        self.pascal_name = "".join(
            word.capitalize() for word in self.authorizer_name.split("_")
        )
        self.secret = "".join(
            random.choices(
                string.ascii_lowercase + string.ascii_uppercase + string.digits, k=52
            )
        )

    def with_config(self, default=False):
        self.config = f"""from infra.services import Services

class {self.pascal_name}Config:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="{self.pascal_name}",
            path="./functions/{self.belongs}",
            description="{self.description}",
            directory="{self.authorizer_name}"
        )

        services.api_gateway.create_authorizer(function, name="{self.authorizer_name}", default={default})
"""
        return self

    def with_main(self):

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
        return self

    def with_unit(self):
        self.unit = f"""from .main import lambda_handler

def test_authorizer_should_pass_with_correct_secret():

    event = {{
        "headers": {{
            "secret": "{self.secret}"
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

    event = {{
        "headers": {{
            "secret": "INVALID-SECRET"
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

    def with_deploy_stage(self):
        self.deploy_stage = self.read_lines("infra/stages/deploy.py")

        folder = f"functions.{self.belongs}.{self.authorizer_name}"

        IMPORT_LINE = 0
        
        self.deploy_stage.insert(
            IMPORT_LINE, f"from {folder}.config import {self.pascal_name}Config\n"
        )

        authorizer_array_index = self.deploy_stage.index('        authorizers = [\n')
        index = authorizer_array_index + 1
        value = f"            {self.pascal_name}Config(self.services),\n"
        if "#" in self.deploy_stage[index]:
            self.deploy_stage[index] = value
        else:
            self.deploy_stage.insert(index, value)

        return self

    def build(self):
        folder_path = self.join("functions", self.belongs, self.authorizer_name)
        self.make_dir(folder_path)
        self.make_dir(f"functions/{self.belongs}/utils")
        self.make_file(self.join("functions", self.belongs), "__init__.py")
        self.make_file(folder_path, "__init__.py")
        self.make_file(f"functions/{self.belongs}/utils", "__init__.py")
        self.make_file(folder_path, "config.py", self.config)
        self.make_file(folder_path, "main.py", self.main)
        self.make_file(folder_path, "unit.py", self.unit)
        self.write_lines("infra/stages/deploy.py", self.deploy_stage)
