import json
from .main import lambda_handler


def test_lambda_handler():

    response = lambda_handler(None, None)

    assert response["body"] == json.dumps({"message": "Hello World!"})
