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
    user_id = "123"

    body = json.loads(event["body"])
    title = body.get("title")
    content = body.get("content")
    created_at = datetime.now().isoformat()

    posts_table.put_item(
        Item={
            "PK": post_id,
            "user_id": user_id,
            "title": title,
            "content": content,
            "comments": [],
            "created_at": created_at,
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"post_id": post_id}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
