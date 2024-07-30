import json
import os
from dataclasses import dataclass

import boto3

from . import utils


@dataclass
class Input:
    pass


@dataclass
class Output:
    message: str


def lambda_handler(event, context):

    dynamodb = boto3.resource("dynamodb")
    VISITED_URLS_TABLE_NAME = os.getenv("VISITED_URLS_TABLE_NAME")
    visited_urls_table = dynamodb.Table(VISITED_URLS_TABLE_NAME)

    sqs_client = boto3.client("sqs")
    CRAWLER_QUEUE_URL = os.getenv("CRAWLER_QUEUE_URL")

    body = json.loads(event["Records"][0]["body"])
    url = body["url"]
    timestamp = body["timestamp"]
    job_id = body["job_id"]
    source_url = body["source_url"]
    root_url = body["root_url"]

    urls_from_page = utils.find_urls_from_page(url)
    filtered_urls = utils.filter_unwanted_urls(urls_from_page, root_url)
    non_visited_urls = utils.get_non_visited_urls(filtered_urls, job_id)

    contents = utils.get_content_from_urls(non_visited_urls)

    utils.save_batch_in_dynamo(
        visited_urls_table, contents, job_id, timestamp, source_url, root_url
    )
    utils.send_batch_to_queue(
        sqs_client,
        CRAWLER_QUEUE_URL,
        non_visited_urls,
        timestamp,
        job_id,
        url,
        root_url,
    )
