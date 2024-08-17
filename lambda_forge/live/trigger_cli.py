import json
import boto3
import requests
from typing import Dict, Literal


ServiceType = Literal["Api Gateway", "SNS", "SQS", "S3", "Event Bridge"]


class LambdaForgeTriggerError(Exception):
    pass


def run_service_api_gateway(data: Dict, _: str):
    if not data.get("url"):
        raise LambdaForgeTriggerError("url is required")

    requests.request(
        data.get("method", "GET"),
        data["url"],
        params=data.get("params", {}),
        headers=data.get("headers", {}),
        data=data.get("body", {}),
    )


def run_service_sns(data: Dict, region: str):
    if not data.get("topic_arn"):
        raise LambdaForgeTriggerError("topic_arn is required")

    sns = boto3.client("sns", region_name=region)
    sns.publish(
        TopicArn=data.get("topic_arn"),
        Message=str(data.get("message")),
        Subject=str(data.get("subject", {})),
    )


def run_service_sqs(data: Dict, region: str):
    if not data.get("queue_url"):
        raise LambdaForgeTriggerError("queue_url is required")

    sqs = boto3.client("sqs", region_name=region)
    sqs.send_message(QueueUrl=data["queue_url"], MessageBody=str(data["message"]))


def run_service_s3(data: Dict, _: str):
    if not data.get("bucket_name") or not data.get("file_path"):
        raise LambdaForgeTriggerError("bucket_name and file_path are required")

    filename = data["file_path"].split("/")[-1]
    s3_client = boto3.client("s3")
    with open(data["file_path"], "rb") as file:
        s3_client.put_object(
            Bucket=data["bucket_name"],
            Key=filename,
            Body=file,
            Metadata=data.get("metadata", {}),
        )


def run_service_event_bridge(data: Dict, region: str):
    if not data.get("bus_name"):
        raise LambdaForgeTriggerError("bus_name is required")

    event = {
        "Source": "event.bridge",
        "DetailType": "UserAction",
        "Detail": json.dumps({"message": data["message"]}),
        "EventBusName": data["bus_name"],
    }
    event_client = boto3.client("events", region_name=region)
    event_client.put_events(Entries=[event])


def run_trigger(service: ServiceType, data: Dict):
    cdk_data = json.load(open("cdk.json", "r"))
    region = cdk_data["context"].get("region")

    if not region:
        raise ValueError("Region Not Found")

    if service == "Api Gateway":
        run_service_api_gateway(data, region)
    elif service == "SNS":
        run_service_sns(data, region)
    elif service == "SQS":
        run_service_sqs(data, region)
    elif service == "S3":
        run_service_s3(data, region)
    elif service == "Event Bridge":
        run_service_event_bridge(data, region)
    else:
        raise LambdaForgeTriggerError("Service not found")
