import json
from .main import lambda_handler


def test_my_lambda_handler():
    event = {
        "Records": [
            {
                "body": json.dumps(
                    {"s3_bucket": "gui-docs", "s3_key": "large_payloads/01b4c589-13fa-466a-aa18-1b1018b43487.json"}
                )
            }
        ]
    }
    lambda_handler(event, None)
