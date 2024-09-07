from .main import lambda_handler


def test_authorizer_should_pass_with_correct_secret():

    event = {
        "headers": {"secret": "CRMdDRMA4iW4xo9l38pACls7zsHYfp8T7TLXtucysb2lB5XBVFn8"},
        "methodArn": "arn:aws:execute-api:us-east-1:123456789012:api-id/stage/GET/resource-path",
    }
    response = lambda_handler(event, None)

    assert response == {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "allow",
                    "Resource": event["methodArn"],
                }
            ],
        },
    }


def test_authorizer_should_fail_with_invalid_secret():

    event = {
        "headers": {"secret": "INVALID-SECRET"},
        "methodArn": "arn:aws:execute-api:us-east-1:123456789012:api-id/stage/GET/resource-path",
    }
    response = lambda_handler(event, None)

    assert response == {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "deny",
                    "Resource": event["methodArn"],
                }
            ],
        },
    }
