# Creating a Guess the Number Game with DynamoDB

In this section, we will develop a "Guess the Number" game. Players will attempt to identify a randomly generated number by making successive guesses.

The architecture of the Lambda functions we are going to create will be as follows:

<p align="center">
  <img src="https://docs.lambda-forge.com/examples/images/guess-the-number.png" alt="alt text">
</p>

## Configuring DynamoDB Tables for Each Deployment Stage

To ensure our application can operate smoothly across different environments, we'll create three separate DynamoDB tables on AWS DynamoDB console, each tailored for a distinct deployment stage: `Dev-Numbers`, `Staging-Numbers` and `Prod-Numbers`.

<div class="admonition note">
<p class="admonition-title">Note</p>
<p>Throughout this tutorial, we'll utilize <b>PK</b> as the Partition Key for all of our DynamoDB tables.</p>
</div>

Having acquired the ARNs for each stage-specific table, our next step involves integrating these ARNs into the `cdk.json` file. This crucial configuration enables our Cloud Development Kit (CDK) setup to correctly reference the DynamoDB tables according to the deployment stage.

Here's how to update your `cdk.json` file to include the DynamoDB table ARNs for development, staging, and production environments:

```json title="cdk.json" linenums="51" hl_lines="3 8 13"
    "dev": {
      "arns": {
        "numbers_table": "$DEV-NUMBERS-TABLE-ARN"
      }
    },
    "staging": {
      "arns": {
        "numbers_table": "$STAGING-NUMBERS-TABLE-ARN"
      }
    },
    "prod": {
      "arns": {
        "numbers_table": "$PROD-NUMBERS-TABLE-ARN"
      }
    }
```

### Incorporating DynamoDB Into the Service Class

The subsequent phase in enhancing our application involves integrating the DynamoDB service within our service layer, enabling direct communication with DynamoDB tables. To accomplish this, utilize the following command:

`forge service dynamodb`

This command creates a new service file named `dynamodb.py` within the `infra/services` directory.

```hl_lines="6"
infra
├── services
    ├── __init__.py
    ├── api_gateway.py
    ├── aws_lambda.py
    └── dynamodb.py
```

Below is the updated structure of our Service class, now including the DynamoDB service, demonstrating the integration's completion:

```python title="infra/services/__init__.py" hl_lines="12"
from infra.services.dynamodb import DynamoDB
from infra.services.api_gateway import APIGateway
from infra.services.aws_lambda import AWSLambda
from infra.services.layers import Layers


class Services:
    def __init__(self, scope, context) -> None:
        self.api_gateway = APIGateway(scope, context)
        self.aws_lambda = AWSLambda(scope, context)
        self.dynamodb = DynamoDB(scope, context)
```

Here is the newly established DynamoDB class:

```python title="infra/services/dynamodb.py"
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_lambda_event_sources as event_source

from lambda_forge.trackers import invoke, trigger


class DynamoDB:
    def __init__(self, scope, context) -> None:

        # self.dynamo = dynamodb.Table.from_table_arn(
        #     scope,
        #     "Dynamo",
        #     context.resources["arns"]["dynamo_arn"],
        # )
        ...

    @trigger(service="dynamodb", trigger="table", function="function")
    def create_trigger(self, table: str, function: lambda_.Function) -> None:
        table_instance = getattr(self, table)
        dynamo_event_stream = event_source.DynamoEventSource(
            table_instance, starting_position=lambda_.StartingPosition.TRIM_HORIZON
        )
        function.add_event_source(dynamo_event_stream)

    @invoke(service="dynamodb", resource="table", function="function")
    def grant_write(self, table: str, function: lambda_.Function) -> None:
        table_instance = getattr(self, table)
        table_instance.grant_write_data(function)

```

Forge has already laid the groundwork by providing a commented code that outlines the structure for creating a DynamoDB table and retrieving its ARN from the `cdk.json` file. Additionally, it's worth noting that the DynamoDB class includes a specialized helper method aimed at streamlining the task of assigning query permissions.

<div class="admonition note">
    <p class="admonition-title">Note</p>
    <p>In this tutorial, we'll manually create AWS resources using the AWS console and directly insert the ARNs into our resource classes to reduce code clutter and simplify understanding. However, feel free to create your AWS resources directly using CDK in the corresponding classes if you prefer.</p>
</div>

Let's refine the class variables to directly reference our Numbers table.

```python title="infra/services/dynamodb.py" hl_lines="4-8" linenums="5"
class DynamoDB:
    def __init__(self, scope, context: dict) -> None:

        self.numbers_table = dynamodb.Table.from_table_arn(
            scope,
            "NumbersTable",
            context.resources["arns"]["numbers_table"],
        )
```

The `context.resources` object on line 11 contains only the resources that are pertinent to the current stage. By tapping into this, we can dynamically tweak our AWS resources according to the specific stage we're operating in.

## Creating a New Game

Now that we have configured the DynamoDB tables, it's time to establish a function for creating new games.

```
forge function create_game --method "POST" --description "Create a new game" --belongs-to guess_the_number --no-tests --endpoint "/games" --public
```

This command initiates the creation of a new function named `create_game` within the `guess_the_number` folder. It specifies that the function will handle `POST` requests and sets the endpoint to `/games`. The function is designated as public, meaning it can be accessed by anyone with the URL.

```
functions
└── guess_the_number
    └── create_game
        ├── __init__.py
        ├── config.py
        └── main.py
```

To create a new game in the database, the process involves receiving a minimum and a maximum number from the user. These values define the range within which a random number will be generated. Subsequently, a unique identifier (UUID) is assigned to the game. The generated random number, along with the UUID, is then saved to the DynamoDB table.

The implementation of this process is outlined below:

```python title="functions/guess_the_number/create_game/main.py"
import json
import os
import random
import uuid
from dataclasses import dataclass

import boto3


@dataclass
class Input:
    min_number: int
    max_number: int


@dataclass
class Output:
    game_id: str


def lambda_handler(event, context):
    # Initialize a DynamoDB resource using the boto3 library
    dynamodb = boto3.resource("dynamodb")
    # Retrieve the DynamoDB table name from environment variables
    NUMBERS_TABLE_NAME = os.environ.get("NUMBERS_TABLE_NAME")
    numbers_table = dynamodb.Table(NUMBERS_TABLE_NAME)

    body = json.loads(event["body"])

    # Get the min and max number from the body
    min_number = body.get("min_number", 1)
    max_number = body.get("max_number", 100)

    # Validate that the initial number is less than the end number
    if min_number >= max_number:
        return {"statusCode": 400, "body": json.dumps({"message": "min_number must be less than max_number"})}

    # Generate a unique game ID using uuid
    game_id = str(uuid.uuid4())
    # Generate a random number between the initial and end numbers
    random_number = random.randint(min_number, max_number)

    # Store the game ID and the random number in DynamoDB
    numbers_table.put_item(
        Item={
            "PK": game_id,
            "number": random_number,
        }
    )

    return {"statusCode": 200, "body": json.dumps({"game_id": game_id})}
```

Next, we need to configure the function to integrate it with the DynamoDB table and set up the appropriate environment variables for accurate table selection.

```python title="functions/guess_the_number/create_game/config.py" hl_lines="12-14 19"
from infra.services import Services


class CreateGameConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="CreateGame",
            path="./functions/guess_the_number",
            description="Creates a new guess the number game",
            directory="create_game",
            environment={
              "NUMBERS_TABLE_NAME": services.dynamodb.numbers_table.table_name
            },
        )

        services.api_gateway.create_endpoint("POST", "/games", function, public=True)

        services.dynamodb.grant_write("numbers_table", function)
```

## Making a Guess

Now that the game is set up in our table, we can begin the guessing phase. Depending on the user's input, the system will respond with `correct`, `higher` or `lower` to guide the user on how their guess compares to the actual number.

```
forge function make_guess --method "GET" --description "Make a guess for a particular game" --belongs-to guess_the_number --no-tests --endpoint "/games/{game_id}" --public
```

This command establishes a new function called `make_guess` in the `guess_the_number` folder. It is configured to handle `GET` requests and utilizes the endpoint `/games/{game_id}`, which requires the game ID to be included in the URL. The function is marked as public, allowing anyone with the URL to access it.

```
functions
└── guess_the_number
    ├── create_game
    │   ├── __init__.py
    │   ├── config.py
    │   └── main.py
    └── make_guess
        ├── __init__.py
        ├── config.py
        └── main.py
```

To implement the guess function, we need to receive a user's guess as a query parameter and compare it with the actual number stored in the database. Based on this comparison, we will return the appropriate response to guide the user.

```python title="functions/guess_the_number/make_guess/main.py"
import json
import os
from dataclasses import dataclass

import boto3


@dataclass
class Path:
    game_id: str


@dataclass
class Input:
    guess: int


@dataclass
class Output:
    answer: str


# Main handler function for the Lambda to process incoming requests
def lambda_handler(event, context):
    # Initialize a DynamoDB resource using boto3 and get the table name from environment variables
    dynamodb = boto3.resource("dynamodb")
    NUMBERS_TABLE_NAME = os.environ.get("NUMBERS_TABLE_NAME")
    numbers_table = dynamodb.Table(NUMBERS_TABLE_NAME)

    # Extract the game_id from path parameters in the event object
    game_id = event["pathParameters"]["game_id"]
    # Extract the guess number from query string parameters in the event object
    guess = event["queryStringParameters"]["guess"]

    # Retrieve the item from DynamoDB based on the game_id
    response = numbers_table.get_item(Key={"PK": game_id})
    # Extract the stored random number from the response
    random_number = int(response["Item"]["number"])

    # Compare the guess to the random number and prepare the answer
    if int(guess) == random_number:
        answer = "correct"
    elif int(guess) < random_number:
        answer = "higher"
    else:
        answer = "lower"

    return {"statusCode": 200, "body": json.dumps({"answer": answer})}
```

Now, let's configure the necessary settings to enable data retrieval from the numbers table in DynamoDB.

```python title="functions/guess_the_number/make_guess/config.py" hl_lines="12-14 19"
from infra.services import Services


class MakeGuessConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="MakeGuess",
            path="./functions/guess_the_number",
            description="Make a guess for a particular game",
            directory="make_guess",
            environment={
                "NUMBERS_TABLE_NAME": services.dynamodb.numbers_table.table_name
            },
        )

        services.api_gateway.create_endpoint("GET", "/games/{game_id}", function, public=True)

        services.dynamodb.numbers_table.grant_read_data(function)
```

## Deploying the Functions

Next, we'll commit our code and push it to GitHub, following these steps:

```bash
# Send your changes to stage
git add .

# Commit with a descriptive message
git commit -m "Guess The Number Game"

# Push changes to the 'dev' branch
git push origin dev

# Merge 'dev' into 'staging' and push
git checkout staging
git merge dev
git push origin staging

# Finally, merge 'staging' into 'main' and push
git checkout main
git merge staging
git push origin main
```

This workflow ensures that our code moves sequentially through the development, staging, and production environments, triggering our three distinct deployment pipelines.

![Pipelines running](images/three_example_pipelines.png)

Upon completion of these pipelines, the Guess The Number game is deployed and available across all environments.

## Testing The Functions

We've deployed our function across three distinct environments. For simplicity, this document will focus on the `dev` environment, though the steps described are directly applicable to the other environments as well.

### Initiating a Game Session

To begin testing, we initiate a game session by sending a POST request to create a new game with a number range from 1 to 10.

```bash
curl --request POST \
  --url 'https://api.lambda-forge.com/dev/games' \
  --header 'Content-Type: application/json' \
  --data '{
	"min_number": 1,
	"max_number": 10
}'
```

This request generates the following response, including a unique Game ID:

```json
{
  "game_id": "794eb9ec-79ae-4b56-9523-2fc8d38c341a"
}
```

### Making Guesses

Now, with our game created and the ID acquired, we proceed by making guesses to find the correct number.

#### First Guess: 1

```
curl --request GET \
  --url 'https://api.lambda-forge.com/dev/games/794eb9ec-79ae-4b56-9523-2fc8d38c341a?guess=1' \
```

Response:

```json
{
  "answer": "higher"
}
```

#### Second Guess: 3

```
curl --request GET \
  --url 'https://api.lambda-forge.com/dev/games/794eb9ec-79ae-4b56-9523-2fc8d38c341a?guess=3' \
```

Response:

```json
{
  "answer": "lower"
}
```

Given the responses, the correct number must be 2. Let's confirm by making the final guess.

#### Final Guess: 2

```
curl --request GET \
  --url 'https://api.lambda-forge.com/dev/games/794eb9ec-79ae-4b56-9523-2fc8d38c341a?guess=2' \
```

Response:

```json
{
  "answer": "correct"
}
```

🎉 Success! The Guess The Number game is functioning perfectly across all environments, confirming the reliability and effectiveness of our deployment strategy.
