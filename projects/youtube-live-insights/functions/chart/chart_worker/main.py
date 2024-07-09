import json
import os

import boto3

from . import utils


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")
    TRANSCRIPTIONS_TABLE_NAME = os.environ.get("TRANSCRIPTIONS_TABLE_NAME")
    transcriptions_table = dynamodb.Table(TRANSCRIPTIONS_TABLE_NAME)

    body = json.loads(event["Records"][0]["body"])

    s3 = boto3.client("s3")
    s3_bucket = body["s3_bucket"]
    s3_key = body["s3_key"]
    s3_object = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    payload = json.loads(s3_object["Body"].read().decode("utf-8"))

    video_id = payload["video_id"]
    label = payload["label"]
    interval = payload["interval"]
    min_messages = payload["min_messages"]
    author_summary = payload["prompt"]
    chat = payload["messages"]

    messages = [message["message"] for message in chat]

    if len(messages) < int(min_messages):
        response = {
            "rating": "0",
            "reason": "Minimum number of messages not reached.",
            "chat_summary": "N/A",
        }

    else:
        response = utils.analyse_with_openai(author_summary, messages)

    transcriptions_table.put_item(
        Item={
            "PK": f"{video_id}#INTERVAL={interval}",
            "SK": label,
            "messages": messages,
            "rating": response["rating"],
            "reason": response["reason"],
            "chat_summary": response["chat_summary"],
        }
    )
