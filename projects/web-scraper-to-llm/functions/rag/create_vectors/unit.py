import json
from .main import lambda_handler


def test_llm_lambda_handler():
    event = {
        "body": json.dumps({
            "job_id": "c5dd8327-64ed-48d4-a3a7-b9a64f5c85c9",
            "index_name": "textualize"
        })
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
