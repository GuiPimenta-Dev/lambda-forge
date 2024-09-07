import base64
import json
import os
from dataclasses import dataclass

import boto3


@dataclass
class Path:
    post_id: str


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    POSTS_TABLE_NAME = os.environ.get("POSTS_TABLE_NAME", "Dev-Blog-Posts")
    dynamodb = boto3.resource("dynamodb")
    posts_table = dynamodb.Table(POSTS_TABLE_NAME)

    post_id = event.get("pathParameters", {}).get("post_id")

    post = posts_table.get_item(Key={"PK": post_id}).get("Item")

    # update a post feature
    body = base64.b64decode(event["body"]).decode("utf-8")

    # Parse the body to extract file content and file name
    boundary = body.split("\n")[0].strip()
    parts = body.split(boundary)

    title = None
    file_content = None

    for part in parts:
        if 'Content-Disposition: form-data; name="file_content"' in part:
            file_content = part.split("\r\n\r\n")[1].strip()
        elif 'Content-Disposition: form-data; name="title"' in part:
            title = part.split("\r\n\r\n")[1].strip()

    if not title or not file_content:
        raise ValueError("File name or content not found in the request")

    post["title"] = title
    post["content"] = file_content

    posts_table.put_item(Item={**post})

    return {
        "statusCode": 201,
        "body": json.dumps({"post_id": post_id}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
