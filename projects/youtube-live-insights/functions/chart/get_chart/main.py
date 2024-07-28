import json
import os
from dataclasses import dataclass
from typing import List, Optional

import boto3

from . import utils


@dataclass
class Input:
    video_id: str
    interval: Optional[int] = 10


@dataclass
class Video:
    publish_date: str
    url: str
    duration: str
    language: str
    title: str


@dataclass
class ChatData:
    chat_summary: str
    rating: int
    reason: str
    messages: List[str]


@dataclass
class Output:
    video: Video
    data: List[ChatData]


def lambda_handler(event, context):

    video_id = event["queryStringParameters"]["video_id"]
    interval = int(event["queryStringParameters"].get("interval", 10))

    dynamodb = boto3.resource("dynamodb")
    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME", "Prod-Live-Insights-Live-Transcriptions")
    VIDEOS_TABLE_NAME = os.environ.get("VIDEOS_TABLE_NAME", "Dev-Videos")

    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)
    videos_table = dynamodb.Table(VIDEOS_TABLE_NAME)

    video = videos_table.get_item(Key={"PK": video_id})["Item"]

    data = utils.query_all_items(transcriptions_table, video_id, interval)
    data = utils.subtract_hours_from_utc(data, hour=3)

    data = {"video": video, "data": data}

    current_dir = os.path.dirname(__file__)
    with open(os.path.join(current_dir, "chart.html")) as f:
        html = f.read()

    html = html.replace("'{{ data }}'", json.dumps(data, default=str))

    return {
        "statusCode": 200,
        "body": html,
        "headers": {"Content-Type": "text/html", "Access-Control-Allow-Origin": "*"},
    }
