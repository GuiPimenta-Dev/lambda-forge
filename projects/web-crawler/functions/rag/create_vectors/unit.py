from .main import lambda_handler


def test_llm_lambda_handler():
    event = {
        "body": {
            "job_id": "0da893aa-7fc0-4c0a-9d5a-dd2528f98a73",
        }
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
