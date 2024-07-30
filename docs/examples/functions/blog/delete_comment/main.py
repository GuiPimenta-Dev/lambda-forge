import json
import os
from dataclasses import dataclass

import boto3


@dataclass
class Path:
    post_id: str


@dataclass
class Input:
    comment_id: str


@dataclass
class Output:
    pass


def lambda_handler(event, context):

    post_id = event.get("pathParameters", {}).get("post_id")

    body = json.loads(event.get("body"))
    comment_id = body.get("comment_id")

    email = event["requestContext"]["authorizer"]["email"]

    POSTS_TABLE_NAME = os.environ.get("POSTS_TABLE_NAME", "Dev-Blog-Posts")
    dynamodb = boto3.resource("dynamodb")
    posts_table = dynamodb.Table(POSTS_TABLE_NAME)

    post = posts_table.get_item(Key={"PK": post_id}).get("Item")
    comments = post.get("comments", [])

    comment = next(
        (comment for comment in comments if comment["comment_id"] == comment_id), None
    )
    if comment["email"] != email:
        return {
            "statusCode": 403,
            "body": {"message": "You are not allowed to delete this comment"},
            "headers": {"Access-Control-Allow-Origin": "*"},
        }

    post["comments"] = [c for c in comments if c["comment_id"] != comment_id]

    posts_table.put_item(Item={**post})

    return {"statusCode": 204, "headers": {"Access-Control-Allow-Origin": "*"}}
