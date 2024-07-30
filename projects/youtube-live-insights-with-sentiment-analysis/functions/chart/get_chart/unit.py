import json
from .main import lambda_handler


def test_my_lambda_handler():
    event = {
        "queryStringParameters": {
            "video_id": "13f1ff34-5ef2-498c-9af0-f2c5c46e12b8",
            "interval": 10,
        }
    }
    lambda_handler(event, None)
