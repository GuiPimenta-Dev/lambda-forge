import boto3
import pytest
from moto import mock_dynamodb, mock_s3, mock_sns, mock_sqs, mock_transcribe


def simplify_dynamodb_item(item):
    simple_item = {}
    for key, value in item.items():
        for _, data_value in value.items():
            simple_item[key] = data_value
    return simple_item


@pytest.fixture
def sqs():
    with mock_sqs():
        yield boto3.client("sqs")


@pytest.fixture
def table():
    with mock_dynamodb():
        dynamodb = boto3.client("dynamodb")
        dynamodb.create_table(
            TableName="table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        yield dynamodb


@pytest.fixture
def sk_table():
    with mock_dynamodb():
        dynamodb = boto3.client("dynamodb")
        dynamodb.create_table(
            TableName="table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        yield dynamodb


@pytest.fixture
def s3():
    with mock_s3():
        s3 = boto3.client("s3", region_name="us-east-2")
        s3.create_bucket(Bucket="bucket")
        yield s3


@pytest.fixture
def sns():
    with mock_sns():
        yield boto3.client("sns")


@pytest.fixture
def transcribe():
    with mock_transcribe():
        yield boto3.client("transcribe")
