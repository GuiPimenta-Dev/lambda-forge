import json
import os

import pytest

from .main import lambda_handler


@pytest.fixture
def transcript_queue(sqs):
    sqs.create_queue(QueueName="transcript_queue")
    response = sqs.get_queue_url(QueueName="transcript_queue")
    queue_url = response["QueueUrl"]
    os.environ["TRANSCRIPT_QUEUE_URL"] = queue_url
    yield sqs


@pytest.mark.skip
def test_create_chart():

    os.environ["CHAT_TABLE_NAME"] = "Dev-Chats"

    event = {
        "pathParameters": {"video_id": "5548f4c0-f5bb-49c9-a026-0f65ef10c412"},
        "body": json.dumps({"interval": 10, "min_messages": 20, "prompt": ""}),
    }

    response = lambda_handler(event, None)

    assert response["body"] == json.dumps({"message": "Hello World!"})
