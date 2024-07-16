import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime

import boto3


@dataclass
class Input:
    url: str


@dataclass
class Output:
    job_id: str
    

def lambda_handler(event, context):
    sqs = boto3.resource("sqs")
    CRAWLER_QUEUE_NAME = os.getenv("CRAWLER_QUEUE_NAME")
    queue = sqs.get_queue_by_name(QueueName=CRAWLER_QUEUE_NAME)

    body = json.loads(event["body"])
    url = body["url"]

    timestamp = datetime.now().isoformat()
    job_id = str(uuid.uuid4())
    print(f"Initiating job {job_id} at {timestamp} for root url {url}")

    data = {"url": url, "timestamp": timestamp, "job_id": job_id, "source_url": None, "root_url": url}
    queue.send_message(MessageBody=json.dumps(data, default=str))

    return {
        "statusCode": 200,
        "body": json.dumps({"job_id": job_id}),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
