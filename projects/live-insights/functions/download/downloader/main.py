import json
import os
from dataclasses import dataclass
from io import BytesIO

import boto3
from pytube import YouTube


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    VIDEOS_TABLE_NAME = os.environ.get("VIDEOS_TABLE_NAME", "Dev-Videos")
    VIDEOS_TOPIC_ARN = os.environ.get("VIDEOS_TOPIC_ARN")

    body = json.loads(event["Records"][0]["body"])
    url = body["url"]
    video_id = body["video_id"]
    language = body["language"]

    yt = YouTube(url)

    duration_in_seconds = yt.length
    hours, remainder = divmod(duration_in_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_formatted = f"{hours:02}:{minutes:02}:{seconds:02}"

    dynamodb = boto3.resource("dynamodb")
    videos_table = dynamodb.Table(VIDEOS_TABLE_NAME)

    videos_table.put_item(
        Item={
            "PK": video_id,
            "url": url,
            "title": yt.title,
            "language": language,
            "publish_date": yt.publish_date.isoformat(),
            "duration": duration_formatted,
        }
    )

    print(f"Publishing video {video_id} to SNS topic {VIDEOS_TOPIC_ARN}")

    sns_client = boto3.client("sns")
    sns_client.publish(
        TopicArn=VIDEOS_TOPIC_ARN,
        Message=json.dumps({"video_id": video_id, "url": url}),
    )
