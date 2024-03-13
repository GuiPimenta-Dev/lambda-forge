import os

import boto3
from botocore.exceptions import ClientError

API_ARN = os.environ["API_ARN"]


def get_authorizer_secret():
    secret_name = "AuthorizerSecret"
    region_name = "us-east-2"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    return get_secret_value_response["SecretString"]


def lambda_handler(event, context):
    if (
        event["headers"].get("secret")
        and event["headers"].get("secret") == get_authorizer_secret()
    ):
        effect = "allow"
        message = "success"
    else:
        # TODO: Create your own authorizer logic here
        effect = "deny"
        message = "invalid secret"

    context = {"message": message}
    policy = {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": API_ARN,
                }
            ],
        },
        "context": context,
    }

    return policy
