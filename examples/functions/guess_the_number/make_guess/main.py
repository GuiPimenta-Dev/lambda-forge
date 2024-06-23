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