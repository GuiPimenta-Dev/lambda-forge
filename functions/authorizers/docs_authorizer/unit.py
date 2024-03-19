from .main import lambda_handler


def test_authorizer_should_pass_with_correct_secret():

    event = {
        "headers": {"secret": "0U44FxLKs0G86qVR69sY2zLjG7C1XFS835MJuNfe0BOvjeS09JwO"}
    }
    response = lambda_handler(event, None)

    assert response == {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": "allow", "Resource": "*"}
            ],
        },
    }


def test_authorizer_should_fail_with_invalid_secret():

    event = {"headers": {"secret": "INVALID-SECRET"}}
    response = lambda_handler(event, None)

    assert response == {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": "deny", "Resource": "*"}
            ],
        },
    }
