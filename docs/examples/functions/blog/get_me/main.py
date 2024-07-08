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
    first_name = event["requestContext"]["authorizer"]["first_name"]
    last_name = event["requestContext"]["authorizer"]["last_name"]
    picture = event["requestContext"]["authorizer"]["picture"]

    return {
        "statusCode": 200,
        "body": json.dumps({"email": email, "first_name": first_name, "last_name": last_name, "picture": picture}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
