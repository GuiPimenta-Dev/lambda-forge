# Utilizing Lambda Layers for Code Reuse and External Library Integration

## What Are Lambda Layers?

Lambda Layers are essentially ZIP archives containing libraries, custom runtime environments, or other dependencies. You can include these layers in your Lambda function’s execution environment without having to bundle them directly with your function's deployment package. This means you can use libraries or custom runtimes across multiple Lambda functions without needing to include them in each function’s codebase.

### How They Work

When you create a Lambda function, you specify which layers to include in its execution environment. During execution, AWS Lambda configures the function's environment to include the content of the specified layers. This content is available to your function's code just as if it were included in the deployment package directly.

### Use Cases

- **Sharing code**: Commonly used code can be placed in a layer and shared among multiple functions.
- **Custom runtimes**: You can use layers to deploy functions in languages that AWS Lambda does not natively support by including the necessary runtime in a layer.
- **Configuration files**: Layers can be used to store configuration files that multiple functions need to access.

## AWS Lambda Development with Custom Layers

Forge streamlines the process of creating and sharing custom layers across AWS Lambda functions, significantly simplifying code reuse and management. This section walks you through creating a custom layer using Forge, integrating it into your development workflow, and utilizing it within a Lambda function.

### Creating a Custom Layer

To begin, execute the following command to create a custom layer named `my_custom_layer`:

```bash
forge layer --custom my_custom_layer
```

This command sets up a specific directory structure for your layer within your project, organizing the code efficiently:

```
layers
├── __init__.py
└── my_custom_layer
    ├── __init__.py
    └── my_custom_layer.py
```

Forge not only initializes the necessary structure but also populates my_custom_layer.py with a starter function. This function acts as a blueprint for your shared code:

```python title="layers/my_custom_layer/my_custom_layer.py"
def hello_from_layer():
    return "Hello from my_custom_layer layer!"
```

Additionally, Forge sets the new custom layer in the Layers class.

```python title="infra/services/layers.py" hl_lines="8-14"
from aws_cdk import aws_lambda as _lambda
from lambda_forge.path import Path


class Layers:
    def __init__(self, scope) -> None:

        self.my_custom_layer = _lambda.LayerVersion(
            scope,
            id='MyCustomLayer',
            code=_lambda.Code.from_asset(Path.layer('layers/my_custom_layer')),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='',
         )
```

Traditionally, working with Lambda layers introduces complexity during development. Since Lambda layers are deployed as zip files and run within the Lambda execution environment, developers usually face challenges in utilizing these layers locally. This often leads to a disconnect between development and production environments, complicating the development process.

==When you create a custom layer using Forge, the new layer is automatically integrated into your local virtual environment, similar to installing an external library from pip.== However, to ensure that these changes are fully recognized, you may need to reload your IDE or reselect your virtual environment.

<div class="admonition note">
<p class="admonition-title">Note</p>
In case you need to reinstall the custom layers into your virtual environment, use the command:

```
forge layer --install
```

</div>

### Creating a Lambda Function Utilizing the Custom Layer

Create a new Lambda function that leverages your custom layer by running:

```
forge function custom --method "GET" --description "A function that uses my_custom_layer" --public
```

This command simply creates a public function named `custom` inside the `functions` directory.

```
functions
└── custom
    ├── __init__.py
    ├── config.py
    ├── integration.py
    ├── main.py
    └── unit.py
```

Now, implement the function to utilize the custom layer:

```python title="functions/layers/custom/main.py" hl_lines="4 19"
import json
from dataclasses import dataclass

import my_custom_layer


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    message = my_custom_layer.hello_from_layer()

    return {"statusCode": 200, "body": json.dumps({"message": message})}
```

Finally, configure the function to make use of the `my_custom_layer` layer:

```python title="functions/layers/custom/config.py" hl_lines="11"
from infra.services import Services


class CustomConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Custom",
            path="./functions/custom",
            description="A function to make use of the custom layer",
            layers=[services.layers.my_custom_layer],
        )

        services.api_gateway.create_endpoint("GET", "/custom", function, public=True)
```

Once you've committed and pushed your code to GitHub and the pipeline has successfully executed, making a GET request to the generated URL should return the following response:

```json
{
  "message": "Hello from my_custom_layer layer!"
}
```

The URL for this tutorial is:

- [https://tbd4it3lph.execute-api.us-east-2.amazonaws.com/dev/custom](https://tbd4it3lph.execute-api.us-east-2.amazonaws.com/dev/custom)

## AWS Lambda Development with External Libraries

In software development, using external libraries is a common practice to extend functionality and streamline the development process. When working with AWS Lambda, incorporating these external libraries requires integrating them as layers into our Lambda functions.

To illustrate this scenario, we will develop a new lambda function aimed to parsing the data retrieved from the external API [https://randomuser.me/api/](https://randomuser.me/api/), a public service for generating random fake user data. Since the `requests` library is not inherently included in Python, it will be necessary to integrate it as a layer in our lambda function.

To create an external layer, run the following command in your terminal:

```
forge layer --external $LAYER
```

### Incorporating Requests from Public Layers

To create a new layer for the requests library, simply run:

```
forge layer --external requests
```

Lambda Forge will automatically create and deploy this layer to AWS, additionally it updates the `Layer` class to utilize your newly created layer.

```python title="infra/services/layers.py" hl_lines="12-16" linenums="6"

class Layers:
    def __init__(self, scope) -> None:

        self.my_custom_layer = _lambda.LayerVersion(
            scope,
            id='MyCustomLayer',
            code=_lambda.Code.from_asset(Path.layer('layers/my_custom_layer')),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='',
         )
        
        self.requests_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope,
            id='RequestsLayer',
            layer_version_arn='arn:aws:lambda:us-east-2:211125768252:layer:requests:1',
         )
```

### Creating a Lambda Function Utilizing the Requests Library

To create a Lambda function that leverages the Requests library, execute the following command:

```
forge function external --method "GET" --description "A function that uses an external library" --public
```

This command creates a new function named `external` inside the functions directory.

```
functions
└── external
    ├── __init__.py
    ├── config.py
    ├── integration.py
    ├── main.py
    └── unit.py
```

Now, implement the function to utilize the custom layer:

```python
import json
from dataclasses import dataclass

import requests


@dataclass
class Input:
    pass


@dataclass
class Name:
    title: str
    first: str
    last: str


@dataclass
class Output:
    name: Name
    gender: str
    email: str


def lambda_handler(event, context):

    result = requests.get("https://randomuser.me/api").json()["results"][0]

    data = {
        "name": result["name"],
        "gender": result["gender"],
        "email": result["email"],
    }

    return {"statusCode": 200, "body": json.dumps({"data": data})}
```

Additionally, update the unit tests to expect the correct output message:

```python title="functions/layers/external/unit.py" hl_lines="10"
import json
from .main import lambda_handler


def test_lambda_handler():

    response = lambda_handler(None, None)
    body = json.loads(response["body"])

    assert ["name", "gender", "email"] == list(body.keys())
```

Finally, configure the function to make use of the requests layer:

```python title="functions/layers/custom/config.py" hl_lines="11"
from infra.services import Services


class ExternalConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="External",
            path="./functions/external",
            description="A function that uses an external library",
            layers=[services.layers.requests_layer],
        )

        services.api_gateway.create_endpoint("GET", "/external", function, public=True)
```

Once you've committed and pushed your code to GitHub and the pipeline has successfully executed, making a GET request to the generated URL should return the following response:

```json
{
  "name": {
    "title": "str",
    "first": "str",
    "last": "str"
  },
  "gender": "str",
  "email": "str"
}
```

For this tutorial, the generated URL is:

- [https://tbd4it3lph.execute-api.us-east-2.amazonaws.com/dev/external](https://tbd4it3lph.execute-api.us-east-2.amazonaws.com/dev/external)
