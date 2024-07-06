import json
import os
from dataclasses import dataclass

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

        items = sorted(response.get("Items", []), key=lambda x: x["created_at"], reverse=True)[:LIMIT]

        last_evaluated_key = response.get("LastEvaluatedKey", None)
        if last_evaluated_key:
            last_evaluated_key = last_evaluated_key["PK"]

        body = {"items": items, "last_evaluated_key": last_evaluated_key}

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
