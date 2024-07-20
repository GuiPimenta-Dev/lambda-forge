import json

import boto3


def get_secret(secret_name: str):
    sm_client = boto3.client("secretsmanager")
    response = sm_client.get_secret_value(SecretId=secret_name)

    try:
        secret = json.loads(response["SecretString"])

    except json.JSONDecodeError:
        secret = response["SecretString"]

    return secret