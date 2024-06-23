import json

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