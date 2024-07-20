from .main import lambda_handler


def test_lambda_handler():
    event = {
        "body": {
            "job_id": "a935b50c-f705-4347-8c8b-bee850311c98",
            "name": "lambda-forge"
        }
    }
    assert lambda_handler(event, None) == {
        "statusCode": 200,
        "body": '{"message": "Hello World!"}',
        "headers": {"Access-Control-Allow-Origin": "*"}
    }