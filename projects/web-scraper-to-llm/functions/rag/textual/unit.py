import json

from .main import lambda_handler


def test_lambda_handler():

    response = lambda_handler(None, None)

    assert response["statusCode"] == 200
