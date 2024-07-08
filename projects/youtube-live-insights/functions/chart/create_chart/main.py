import json
from dataclasses import dataclass
from typing import Optional

from . import utils


@dataclass
class Path:
    video_id: str


@dataclass
class Input:
    prompt: Optional[str] = ""
    interval: Optional[int] = 10
    min_messages: Optional[int] = 20


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    body = event["Records"][0]["body"]

    body = json.loads(body)

    video_id = body.get("video_id")
    interval = body.get("interval", 10)
    min_messages = body.get("min_messages", 20)
    prompt = body.get("prompt", "")

    batches = utils.group_chat_by_interval(partition_key=video_id, interval=interval)

    for index, batch in enumerate(batches):
        utils.send_message_to_sqs(video_id, batch, batches, interval, index, min_messages, prompt)

    return {"statusCode": 200, "body": json.dumps({"message": "ok!"}), "headers": {"Access-Control-Allow-Origin": "*"}}
