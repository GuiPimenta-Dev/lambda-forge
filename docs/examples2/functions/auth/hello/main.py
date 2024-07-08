import json
from dataclasses import dataclass


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    email = event["requestContext"]["authorizer"]["email"]

    return {"statusCode": 200, "body": json.dumps({"message": f"Hello, {email}!"})}
