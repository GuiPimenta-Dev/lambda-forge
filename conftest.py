import json
import os
import random
import string

import boto3
import moto
import pytest
from botocore.exceptions import ClientError


@pytest.fixture
def rand_string():
    def random_string(length=5):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    return random_string


@pytest.fixture
def table():
    with moto.mock_dynamodb():
        db = boto3.client("dynamodb")
        db.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
            ],
            TableName="MOCKED_TABLE",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        table = boto3.resource("dynamodb").Table("MOCKED_TABLE")
        yield table


@pytest.fixture
def headers():
    secret_name = "AuthorizerSecret"
    region_name = "us-east-2"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    return {"secret": secret, "origin": "*"}


@pytest.fixture
def env():
    os.environ["CONTROL_TABLE_NAME"] = "MOCKED_TABLE"


@pytest.fixture
def control_table():
    dynamodb = boto3.resource("dynamodb")
    control_table = dynamodb.Table("EntriControlServerDev")
    return control_table


def pytest_generate_tests(metafunc):
    for mark in metafunc.definition.iter_markers(name="integration"):
        with open("tested_endpoints.jsonl", "a") as f:
            f.write(f"{json.dumps(mark.kwargs)}\n")
