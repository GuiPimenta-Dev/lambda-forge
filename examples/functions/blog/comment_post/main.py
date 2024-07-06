import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime

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

    dynamodb = boto3.resource("dynamodb")
    POSTS_TABLE_NAME = os.environ.get("POSTS_TABLE_NAME", "Dev-Blog-Posts")
    posts_table = dynamodb.Table(POSTS_TABLE_NAME)

    comment_id = str(uuid.uuid4())
    post_id = event.get("pathParameters", {}).get("post_id")

    user_id = "123"

    body = json.loads(event["body"])
    comment = body.get("comment")
    created_at = datetime.now().isoformat()
    post = posts_table.get_item(Key={"PK": post_id}).get("Item")
    comment = {
        "comment": comment,
        "user_id": user_id,
        "created_at": created_at,
    }
    post["comments"].append(comment)

    posts_table.put_item(Item={**post})

    return {
        "statusCode": 201,
        "body": json.dumps({"comment_id": comment_id}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
