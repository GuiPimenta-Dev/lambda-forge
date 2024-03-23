import random
import string
from lambda_forge.builders.file_service import FileService


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
        if not self.pascal_name.endswith("Authorizer"):
            self.pascal_name += "Authorizer"
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
            path="./authorizers/{self.authorizer_name}",
            description="{self.description}"
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

    def with_lambda_stack(self):
        self.lambda_stack = self.read_lines("infra/stacks/lambda_stack.py")

        folder = f"authorizers.{self.authorizer_name}"

        self.lambda_stack.insert(
            0, f"from {folder}.config import {self.pascal_name}Config\n"
        )

        comment = "".join(word.capitalize() for word in self.belongs.split("_"))

        try:
            comment_index = self.lambda_stack.index(f"        # {comment}\n")
            self.lambda_stack.insert(
                comment_index + 1,
                f"        {self.pascal_name}Config(self.services)\n",
            )
        except:
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
        folder_path = self.join("authorizers", self.authorizer_name)
        self.make_dir(folder_path)
        self.make_dir("authorizers/utils")
        self.make_file(self.join("authorizers"), "__init__.py")
        self.make_file(folder_path, "__init__.py")
        self.make_file("authorizers/utils", "__init__.py")
        self.make_file(folder_path, "config.py", self.config)
        self.make_file(folder_path, "main.py", self.main)
        self.make_file(folder_path, "unit.py", self.unit)
        self.write_lines("infra/stacks/lambda_stack.py", self.lambda_stack)
