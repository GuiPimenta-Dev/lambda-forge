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

    return {
        "statusCode": 200,
        "body": json.dumps({"game_id": game_id}),
        "headers": {"Access-Control-Allow-Origin": "*"}
    }
