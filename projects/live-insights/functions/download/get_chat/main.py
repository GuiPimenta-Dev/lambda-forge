import datetime
import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from chat_downloader import ChatDownloader as cd


# Function to batch write items to DynamoDB
def batch_write_items(items, table):
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        print("Batch write successful.")
    except ClientError as e:
        print(f"Error occurred: {e.response['Error']['Message']}")


# Function to process chat messages and save in DynamoDB
def process_and_save_chat(chat, video_id, table):
    batch_size = 300
    items_to_write = []
    number_of_messages = 0

    for message in chat:
        timestamp_seconds = message["timestamp"] / 1_000_000
        utc_datetime = datetime.datetime.utcfromtimestamp(timestamp_seconds)
        utc_datetime = utc_datetime.replace(tzinfo=datetime.timezone.utc)
        formatted_date = utc_datetime.strftime("%Y-%m-%d %H:%M:%S %Z%z")

        sk = f"{formatted_date}#ID={str(uuid.uuid4())}"
        item = {
            "PK": video_id,
            "SK": sk,
            "message": message["message"],
            "author": message["author"],
        }

        items_to_write.append(item)
        number_of_messages += 1

        # If batch size limit is reached, write items to DynamoDB
        if len(items_to_write) == batch_size:
            print(f"Inserting batch of {batch_size} items into the table")
            batch_write_items(items_to_write, table)
            items_to_write = []

    # Write remaining items if any
    if items_to_write:
        print(f"Inserting remaining {len(items_to_write)} items into the table")
        batch_write_items(items_to_write, table)

    print(f"Inserted {number_of_messages} messages")
    return number_of_messages


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

    CHAT_TABLE_NAME = os.environ.get("CHAT_TABLE_NAME", "Dev-Chats")
    chats_table = dynamodb.Table(CHAT_TABLE_NAME)

    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    video_id = message["video_id"]
    url = message["url"]

    chat = cd().get_chat(url)

    number_of_messages = process_and_save_chat(chat, video_id, chats_table)

    return {
        "number_of_messages": number_of_messages,
    }
