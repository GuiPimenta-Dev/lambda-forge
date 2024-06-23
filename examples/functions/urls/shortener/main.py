from dataclasses import dataclass
import hashlib
import json
import os
import boto3

@dataclass
class Input:
    url: str


@dataclass
class Output:
    short_url: str


def lambda_handler(event, context):
    # Retrieve DynamoDB table name and the Base URL from environment variables.
    URLS_TABLE_NAME = os.environ.get("URLS_TABLE_NAME")
    BASE_URL = os.environ.get("BASE_URL")

    # Initialize DynamoDB resource.
    dynamodb = boto3.resource("dynamodb")

    # Reference the specified DynamoDB table.
    urls_table = dynamodb.Table(URLS_TABLE_NAME)

    # Parse the URL from the incoming event's body.
    body = json.loads(event["body"])
    original_url = body["url"]

    # Generate a URL hash.
    hash_object = hashlib.sha256(original_url.encode())
    url_id = hash_object.hexdigest()[:6]

    # Store the mapping in DynamoDB.
    urls_table.put_item(Item={"PK": url_id, "original_url": original_url})

    # Construct the shortened URL.
    short_url = f"{BASE_URL}/{url_id}"

    # Return success response.
    return {"statusCode": 200, "body": json.dumps({"short_url": short_url})}