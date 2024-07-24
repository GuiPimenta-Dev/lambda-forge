import json
import os
from datetime import time
from urllib.parse import urljoin

import boto3
import requests
from bs4 import BeautifulSoup


def find_urls_from_page(url):
    response = requests.get(url)
    if not response.ok:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all("a", href=True)
    urls_from_page = [urljoin(url, link["href"]) for link in links]
    print(f"Urls from {url}: {urls_from_page}")
    return urls_from_page


def filter_unwanted_urls(urls, root_url):
    removed_urls = [url for url in urls if not url.startswith(root_url) or "#_" in url]
    print(f"Removed urls: {removed_urls}")
    valid_urls = [url for url in urls if url.startswith(root_url) and "#_" not in url]
    print(f"Valid urls: {valid_urls}")
    return valid_urls


def get_content_from_page(url):
    response = requests.get(url)
    if not response.ok:
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    return soup.text


def get_non_visited_urls(urls, job_id):
    dynamodb = boto3.client("dynamodb")
    VISITED_URLS_TABLE_NAME = os.getenv("VISITED_URLS_TABLE_NAME", "VisitedURLs")
    BATCH_SIZE = 100  # Maximum number of keys to send in each batch
    keys = [{"PK": {"S": job_id}, "SK": {"S": url}} for url in set(urls)]

    non_visited_urls = set(urls)
    unprocessed_keys = keys

    while unprocessed_keys:
        for i in range(0, len(unprocessed_keys), BATCH_SIZE):
            batch_keys = unprocessed_keys[i : i + BATCH_SIZE]
            try:
                response = dynamodb.batch_get_item(RequestItems={VISITED_URLS_TABLE_NAME: {"Keys": batch_keys}})
            except dynamodb.exceptions.ClientError as e:
                print(f"[ERROR] {e}")
                time.sleep(1)  # Sleep briefly to avoid retry storms
                continue

            items = response.get("Responses", {}).get(VISITED_URLS_TABLE_NAME, [])
            for item in items:
                non_visited_urls.discard(item["SK"]["S"])

            unprocessed_keys = response.get("UnprocessedKeys", {}).get(VISITED_URLS_TABLE_NAME, {}).get("Keys", [])

    non_visited_urls = list(non_visited_urls)
    print(f"Non visited urls: {non_visited_urls}")
    return non_visited_urls


def get_content_from_urls(urls):
    items = []
    for url in urls:
        content = get_content_from_page(url)
        items.append({"url": url, "content": content})
    return items


def save_batch_in_dynamo(table, contents, job_id, timestamp, source_url, root_url):
    with table.batch_writer() as batch:
        for content in contents:
            item = {
                "PK": job_id,
                "SK": content["url"],
                "timestamp": timestamp,
                "content": content["content"],
                "source_url": source_url,
                "root_url": root_url,
            }
            print(f"Saving item: {item}")
            batch.put_item(Item=item)


def send_batch_to_queue(sqs_client, queue_url, non_visited_urls, timestamp, job_id, source_url, root_url):
    BATCH_SIZE = 10
    for i in range(0, len(non_visited_urls), BATCH_SIZE):
        batch = non_visited_urls[i : i + BATCH_SIZE]
        entries = [
            {
                "Id": str(i + index),  # Ensure unique IDs across batches
                "MessageBody": json.dumps(
                    {
                        "url": url,
                        "timestamp": timestamp,
                        "job_id": job_id,
                        "source_url": source_url,
                        "root_url": root_url,
                    }
                ),
            }
            for index, url in enumerate(batch)
        ]
        print(f"Sending batch: {entries}")
        response = sqs_client.send_message_batch(QueueUrl=queue_url, Entries=entries)
        print(f"Response: {response}")
