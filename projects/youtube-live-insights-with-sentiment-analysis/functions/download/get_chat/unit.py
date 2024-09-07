import json
import os

import pytest

from .main import lambda_handler


@pytest.fixture
def chats_table(sk_table):
    os.environ["CHAT_TABLE_NAME"] = "table"
    yield sk_table


def test_it_should_save_all_messages_on_dynamo_db(chats_table):

    event = {
        "Records": [
            {
                "Sns": {
                    "Message": json.dumps(
                        {
                            "video_id": "123",
                            "url": "https://www.youtube.com/watch?v=9HQiTFZz0Gg",
                        }
                    )
                }
            }
        ]
    }

    response = lambda_handler(event, None)
    number_of_messages = response["number_of_messages"]

    scan = chats_table.scan(TableName="table")

    scanned_items = len(scan["Items"])
    while True:
        if not "LastEvaluatedKey" in scan:
            break
        scan = chats_table.scan(
            TableName="table", ExclusiveStartKey=scan["LastEvaluatedKey"]
        )
        scanned_items += len(scan["Items"])

    assert scanned_items == number_of_messages
