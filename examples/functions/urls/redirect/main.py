from dataclasses import dataclass
import json
import boto3
import os


@dataclass
class Path:
    url_id: str


@dataclass
class Input:
    pass


@dataclass
class Output:
    pass


def lambda_handler(event, context):

    # Retrieve DynamoDB table name from environment variables.
    URLS_TABLE_NAME = os.environ.get("URLS_TABLE_NAME")

    # Initialize DynamoDB resource and table reference.
    dynamodb = boto3.resource("dynamodb")
    urls_table = dynamodb.Table(URLS_TABLE_NAME)

    # Extract shortened URL identifier from path parameters.
    short_url = event["pathParameters"]["url_id"]

    # Retrieve the original URL using the shortened identifier.
    response = urls_table.get_item(Key={"PK": short_url})
    original_url = response.get("Item", {}).get("original_url")

    # Return 404 if no URL is found for the identifier.
    if original_url is None:
        return {"statusCode": 404, "body": json.dumps({"message": "URL not found"})}

    # Ensure URL starts with "http://" or "https://".
    if not original_url.startswith("http"):
        original_url = f"http://{original_url}"

    # Redirect to the original URL with a 301 Moved Permanently response.
    return {"statusCode": 301, "headers": {"Location": original_url}}