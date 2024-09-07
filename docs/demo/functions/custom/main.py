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

    return {
        "statusCode": 200,
        "body": json.dumps({"message": message}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
