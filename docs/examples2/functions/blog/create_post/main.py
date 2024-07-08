import base64
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime

import boto3


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")

    POSTS_TABLE_NAME = os.environ.get("POSTS_TABLE_NAME", "Dev-Blog-Posts")

    posts_table = dynamodb.Table(POSTS_TABLE_NAME)

    post_id = str(uuid.uuid4())
    email = event["requestContext"]["authorizer"]["email"]

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

    created_at = datetime.now().isoformat()

    posts_table.put_item(
        Item={
            "PK": post_id,
            "email": email,
            "title": title,
            "content": file_content,
            "comments": [],
            "likes": [],
            "created_at": created_at,
        }
    )

    return {
        "statusCode": 201,
        "body": json.dumps({"post_id": post_id}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
