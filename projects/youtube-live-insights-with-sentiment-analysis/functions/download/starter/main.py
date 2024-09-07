import json
import os
import uuid
from dataclasses import dataclass

import boto3


@dataclass
class Input:
    url: str


@dataclass
class Output:
    id: str


def lambda_handler(event, context):

    body = json.loads(event["body"])
    url = body["url"]
    language = body.get("language", "pt-BR")

    video_id = str(uuid.uuid4())

    sqs = boto3.client("sqs", region_name="us-east-2")
    SQS_QUEUE_URL = os.environ.get("DOWNLOADS_QUEUE_URL")
    message = {"url": url, "video_id": video_id, "language": language}
    sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(message))

    return {
        "statusCode": 200,
        "body": json.dumps({"video_id": video_id}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
