import json
import os

import boto3


def get_secret(secret_name: str):

    # Initialize the Secrets Manager client
    sm_client = boto3.client("secretsmanager")

    # Retrieve the secret value from Secrets Manager
    response = sm_client.get_secret_value(SecretId=secret_name)

    # Handle scenarios where the secret is stored as plain text instead of JSON.
    try:
        secret = json.loads(response["SecretString"])

    except json.JSONDecodeError:
        secret = response["SecretString"]

    return secret

def lambda_handler(event, context):

    secret = event["headers"].get("secret")

    AUTHORIZER_SECRET_NAME = os.getenv("AUTHORIZER_SECRET_NAME")
    SECRET = get_secret(AUTHORIZER_SECRET_NAME)

    effect = "allow" if secret == SECRET else "deny"

    policy = {
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{"Action": "execute-api:Invoke", "Effect": effect, "Resource": event["methodArn"]}],
        },
    }
    return policy
