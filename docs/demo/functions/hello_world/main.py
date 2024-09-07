import json
from dataclasses import dataclass


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "hello my friend!"}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
