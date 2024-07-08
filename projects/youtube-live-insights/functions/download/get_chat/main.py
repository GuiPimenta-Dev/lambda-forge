import json
import os

import boto3
from chat_downloader import ChatDownloader as cd

from . import utils


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

    CHAT_TABLE_NAME = os.environ.get("CHAT_TABLE_NAME", "Dev-Chats")
    chats_table = dynamodb.Table(CHAT_TABLE_NAME)

    record = event["Records"][0]
    message = json.loads(record["Sns"]["Message"])

    video_id = message["video_id"]
    url = message["url"]

    chat = cd().get_chat(url)

    number_of_messages = utils.process_and_save_chat(chat, video_id, chats_table)

    return {
        "number_of_messages": number_of_messages,
    }
