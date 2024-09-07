import json

from .main import lambda_handler


def test_lambda_handler():

    event = {
        "queryStringParameters": {
            "query": "What is Textual?",
            "index_name": "textualize"
        }
    }
    response = lambda_handler(event, None)

    assert json.loads(response["body"])["response"] is not None
