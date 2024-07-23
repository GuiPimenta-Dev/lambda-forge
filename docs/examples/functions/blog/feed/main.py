import json
import os
from dataclasses import dataclass
from typing import List

import boto3


@dataclass
class Input:
    pass


@dataclass
class User:
    email: str
    first_name: str
    last_name: str
    picture: str


@dataclass
class Comment:
    comment_id: str
    comment: str
    email: str
    first_name: str
    last_name: str
    picture: str
    created_at: str


@dataclass
class Post:
    post_id: str
    title: str
    content: str
    created_at: str
    comments: List[Comment]
    likes: int
    liked: bool


@dataclass
class Output:
    user: User
    feed: List[Post]
    last_evaluated_key: str


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    POSTS_TABLE_NAME = os.environ.get("POSTS_TABLE_NAME", "Dev-Blog-Posts")
    posts_table = dynamodb.Table(POSTS_TABLE_NAME)

    email = event["requestContext"]["authorizer"]["email"]
    first_name = event["requestContext"]["authorizer"]["first_name"]
    last_name = event["requestContext"]["authorizer"]["last_name"]
    picture = event["requestContext"]["authorizer"]["picture"]

    user = {"email": email, "first_name": first_name, "last_name": last_name, "picture": picture}

    LIMIT = 10
    query = event.get("queryStringParameters", {})
    last_evaluated_key = None
    if query:
        last_evaluated_key = query.get("last_evaluated_key")

    scan_params = {
        "Limit": LIMIT,
    }

    if last_evaluated_key:
        scan_params["ExclusiveStartKey"] = {"PK": last_evaluated_key}

    try:
        response = posts_table.scan(**scan_params)

        feed = sorted(response.get("Items", []), key=lambda x: x["created_at"], reverse=True)[:LIMIT]

        last_evaluated_key = response.get("LastEvaluatedKey", None)
        if last_evaluated_key:
            last_evaluated_key = last_evaluated_key["PK"]

        feed = [
            {
                "post_id": item["PK"],
                "title": item["title"],
                "content": item["content"],
                "created_at": item["created_at"],
                "comments": item["comments"],
                "likes": len(item["likes"]),
                "liked": email in item["likes"],
            }
            for item in feed
        ]

        body = {"user": user, "feed": feed, "last_evaluated_key": last_evaluated_key}

        return {
            "statusCode": 200,
            "body": json.dumps(body),
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)}),
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
        }
