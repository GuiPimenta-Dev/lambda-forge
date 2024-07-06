import json
from dataclasses import dataclass


@dataclass
class Input:
    pass

@dataclass
class Output:
    message: str


def lambda_handler(event, context):
    print(event)
    print(context)
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello World!"}),
        "headers": {"Access-Control-Allow-Origin": "*"}
    }
