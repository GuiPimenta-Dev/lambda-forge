import json
import os
import uuid
from collections import defaultdict
from datetime import datetime, timedelta

import boto3


def query_all_items(table, partition_key):
    items = []
    last_evaluated_key = None

    while True:
        if last_evaluated_key:
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(partition_key),
                ExclusiveStartKey=last_evaluated_key,
            )
        else:
            response = table.query(KeyConditionExpression=boto3.dynamodb.conditions.Key("PK").eq(partition_key))

        items.extend(response["Items"])

        if "LastEvaluatedKey" not in response:
            break

        last_evaluated_key = response["LastEvaluatedKey"]

    return items


def send_message_to_sqs(video_id, batch, batches, interval, index, min_messages, prompt):
    TRANSCRIPT_QUEUE_URL = os.environ.get("TRANSCRIPT_QUEUE_URL")
    BUCKET_NAME = "gui-docs"

    try:
        payload = {
            "video_id": video_id,
            "label": batch,
            "messages": batches[batch],
            "interval": interval,
            "index": index,
            "min_messages": min_messages,
            "prompt": prompt,
        }

        s3_key = upload_to_s3(payload, BUCKET_NAME)
        message_body = json.dumps({"s3_bucket": BUCKET_NAME, "s3_key": s3_key}, default=str)

        sqs = boto3.client("sqs")

        sqs.send_message(
            QueueUrl=TRANSCRIPT_QUEUE_URL,
            MessageBody=message_body,
        )

    except Exception as e:
        print(e)


def upload_to_s3(data, bucket_name):
    s3 = boto3.client("s3")
    key = f"large_payloads/{uuid.uuid4()}.json"
    s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data, default=str))
    return key


def round_time(dt, interval):
    discard = timedelta(minutes=dt.minute % int(interval), seconds=dt.second, microseconds=dt.microsecond)
    return dt - discard


def format_time_label(dt):
    total_minutes = dt.hour * 60 + dt.minute
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{minutes:02d}"


def group_chat_by_interval(partition_key, interval):

    session = boto3.Session()

    dynamodb = session.resource("dynamodb")
    CHAT_TABLE_NAME = os.environ.get("CHAT_TABLE_NAME", "Dev-Chats")
    table = dynamodb.Table(CHAT_TABLE_NAME)

    items = query_all_items(table, partition_key)

    # Group items by 10-minute intervals
    grouped_items = defaultdict(list)
    for item in items:
        sk = item["SK"]
        sk = sk.split("#")[0]
        sk = sk.replace(" UTC+0000", "")
        sk_datetime = datetime.strptime(sk, "%Y-%m-%d %H:%M:%S")
        rounded_time = round_time(sk_datetime)
        time_label = format_time_label(rounded_time)
        grouped_items[time_label].append(item)

    return grouped_items
