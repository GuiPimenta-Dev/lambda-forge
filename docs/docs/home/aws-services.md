# Integrating AWS Services to Lambda Functions

Lambda functions frequently interact with various AWS services. With AWS offering over 200 services, connecting these functions to leverage different services, creating triggers, and assigning the proper permissions can be quite challenging. To address this complexity and to create a scalable architecture that can evolve over time, Lambda Forge employs dependency injection. This approach injects each service with its single responsibility into our functions, simplifying management and enhancing scalability.

## The Services Class

Every AWS resources is defined in separate classes within the `infra/services` folder. When you initiate a new project using `forge project`, this directory is automatically created and populated with two service directories: `api_gateway` and `aws_lambda`. Each file contains template code to facilitate the creation of a Lambda function and its integration with API Gateway.

```
infra
└── services
    ├── __init__.py
    ├── api_gateway.py
    └── aws_lambda.py
```


Within the `infra/services/__init__.py` file, you'll find the `Services` class, a comprehensive resource manager designed to streamline the interaction with AWS services. This class acts as a dependency injector, enabling the easy and efficient configuration of AWS resources.

```python title="infra/services/__init__.py"
from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import AWSLambda

class Services:

    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = AWSLambda(scope, context)
```

## Creating AWS Services

Lambda Forge simplifies working with AWS Lambda functions by providing pre-built classes for common AWS services. To create these classes, use the following command:

`forge service $SERVICE`

Lambda Forge currently has built-in classes for the following AWS services:

<div align="center">
<table>
  <tr>
    <td>API Gateway</td>
    <td>Lambda Layers</td>
  </tr>
  <tr>
    <td>AWS Lambdas</td>
    <td>KMS</td>
  </tr>
  <tr>
    <td>Cognito</td>
    <td>S3</td>
  </tr>
  <tr>
    <td>DynamoDB</td>
    <td>Secrets Manager</td>
  </tr>
  <tr>
    <td>Event Bridge</td>
    <td>SNS</td>
  </tr>
  <tr>
    <td>Websockets</td>
    <td>SQS</td>
  </tr>
</table>
</div>

<div class="admonition note">
<p class="admonition-title">Note</p>
<p>
You can create your own custom classes using CDK for handling other AWS services by following the architecture set by Lambda Forge, which adheres to the Single Responsibility Principle and Dependency Injection. This approach allows you to seamlessly integrate your custom service class into the existing framework.
</p>
</div>

### Example: Creating an SNS Class

To create a class for handling SNS configurations, run `forge service sns`. This command will update your folder structure as shown below:

```hl_lines="6"
infra
└── services
    ├── __init__.py
    ├── api_gateway.py
    ├── aws_lambda.py
    └── sns.py
```

Here's an example of the SNS class provided by Lambda Forge:

```python title="infra/services/sns.py"
from aws_cdk import aws_lambda_event_sources
from aws_cdk import aws_sns as sns

from lambda_forge.trackers import invoke, trigger


class SNS:
    def __init__(self, scope, context) -> None:

        # self.sns_topic = sns.Topic.from_topic_arn(
        #     scope,
        #     id="SNSTopic",
        #     topic_arn=context.resources["arns"]["sns_topic_arn"],
        # )
        ...

    @trigger(service="sns", trigger="topic", function="function")
    def create_trigger(self, topic, function):
        topic = getattr(self, topic)
        sns_subscription = aws_lambda_event_sources.SnsEventSource(topic)
        function.add_event_source(sns_subscription)


    @invoke(service="sns", resource="topic", function="function")
    def grant_publish(self, topic, function):
        topic = getattr(self, topic)
        topic.grant_publish(function)
```


The SNS class provided by Forge includes methods for triggering a lambda and granting it permission to consume a topic. These methods are designed to keep track of these events using the `trigger` and `invoke` decorators.

### Updating Hello World Function to also be Triggered by SNS

For example, let's update our already existent `Hello World` function to be triggered by both the API Gateway and the SNS topic. 

In order to do so, we need modify the SNS class adding the ARN of the real topic from AWS:

```python title="infra/services/sns.py" linenums="7" hl_lines="4-8"
class SNS:
    def __init__(self, scope, context) -> None:

        self.hello_world_topic = sns.Topic.from_topic_arn(
            scope,
            id="HelloWorldTopic",
            topic_arn=context.resources["arns"]["hello_world_topic"],
        )

```

Now we need to define the topic arns for each environment in the `cdk.json` file:

```json title="cdk.json" linenums="50" hl_lines="3 8 13"
    "dev": {
      "arns": {
          "hello_world_topic": "$DEV-SNS-TOPIC"
      }
    },
    "staging": {
        "arns": {
            "hello_world_topic": "$STAGING-SNS-TOPIC",
        }
    },
    "prod": {
        "arns": {
            "hello_world_topic": "$PROD-SNS-TOPIC",
        }
    }
```

Now, change the existing `config.py` file to also use the new SNS topic:

```python title="functions/hello_world/config.py" hl_lines="15"
from infra.services import Services


class HelloWorldConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="HelloWorld",
            path="./functions/hello_world",
            description="A simple hello world",
        )

        services.api_gateway.create_endpoint("GET", "/hello_world", function, public=True)

        services.sns.create_trigger("hello_world_topic", function)
```

Now our hello world function can be triggered by two different sources.

## Tracking the Triggers and Invocations

Every time we run the command `cdk synth`, Lambda Forge tracks the trigger and invocations for each lambda defined in your Lambda Stack and generate a json file called `functions.json` file at the root of your project.

```json title="functions.json"
[
    {
        "name": "HelloWorld",
        "path": "./functions/hello_world",
        "description": "A simple hello world",
        "timeout": 60,
        "triggers": [
            {
                "service": "api_gateway",
                "trigger": "/hello_world",
                "method": "GET",
                "public": true
            },
            {
                "service": "sns",
                "trigger": "hello_world_topic"
            }
        ],
        "invocations": []
    }
]
```

The `functions.json` file is essential to Lambda Forge, serving as a crucial component for many of its features, including documentation generation and custom CodePipeline steps.












