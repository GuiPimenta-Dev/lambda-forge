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
    pass


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")
    POSTS_TABLE_NAME = os.environ.get("POSTS_TABLE_NAME", "Dev-Blog-Posts")
    posts_table = dynamodb.Table(POSTS_TABLE_NAME)

    post_id = event.get("pathParameters", {}).get("post_id")

    posts_table.delete_item(Key={"PK": post_id})

    return {"statusCode": 204, "headers": {"Access-Control-Allow-Origin": "*"}}
