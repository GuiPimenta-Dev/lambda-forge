import json

from .main import lambda_handler


def test_lambda_handler():

    event = {
        "queryStringParameters": {
            "query": "how to make Hello World in lambda forge?",
        }
    }
    response = lambda_handler(event, None)

    assert json.loads(response["body"])["response"] is not None
