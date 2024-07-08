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

    dynamodb = boto3.resource("dynamodb")
    POSTS_TABLE_NAME = os.environ.get("POSTS_TABLE_NAME", "Dev-Blog-Posts")
    posts_table = dynamodb.Table(POSTS_TABLE_NAME)

    post_id = event.get("pathParameters", {}).get("post_id")

    email = event["requestContext"]["authorizer"]["email"]

    post = posts_table.get_item(Key={"PK": post_id}).get("Item")
    likes = post.get("likes", [])

    if email in likes:
        likes.remove(email)
    else:
        likes.append(email)

    post["likes"] = likes
    posts_table.put_item(Item={**post})

    return {"statusCode": 204, "headers": {"Access-Control-Allow-Origin": "*"}}
