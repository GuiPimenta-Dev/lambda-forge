import os

import sm_utils


def lambda_handler(event, context):

    secret = event["headers"].get("secret")

    AUTHORIZER_SECRET_NAME = os.getenv("AUTHORIZER_SECRET_NAME")
    SECRET = sm_utils.get_secret(AUTHORIZER_SECRET_NAME)

    effect = "allow" if secret == SECRET else "deny"

    policy = {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": event["methodArn"],
                }
            ],
        },
    }
    return policy
