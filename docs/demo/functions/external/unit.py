import json

from .main import lambda_handler


def test_lambda_handler():

    response = lambda_handler(None, None)
    body = json.loads(response["body"])

    assert ["gender", "name", "location", "email", "login", "phone"] == list(body.keys())
