import time
import click
import requests
from lambda_forge.printer import Printer
import json
from InquirerPy import get_style, inquirer
import boto3

printer = Printer()


def run_trigger():
    data = json.load(open("cdk.json", "r"))
    region = data["context"].get("region")

    if not region:
        printer.print("Region Not Found", "red", 1, 1)
        exit()

    while True:
        printer.show_banner("Live Trigger")
        printer.br()
        options = sorted(["Api Gateway", "SNS", "SQS", "S3", "Event Bridge"])
        style = get_style(
            {
                "questionmark": "#25ABBE",
                "input": "#25ABBE",
                "pointer": "#25ABBE",
                "question": "#ffffff",
                "answered_question": "#25ABBE",
                "pointer": "#25ABBE",
                "answer": "white",
                "answermark": "#25ABBE",
            },
            style_override=True,
        )
        service = inquirer.select(
            message="Select a Trigger:",
            style=style,
            choices=options,
        ).execute()

        try:
            if service == "Api Gateway":
                initial_text = json.dumps(
                    {
                        "method": "GET",
                        "url": "",
                        "params": {},
                        "body": {},
                        "headers": {},
                    },
                    indent=2,
                )
                data = click.edit(text=initial_text)
                data = json.loads(data)
                if not data.get("url"):
                    printer.print("url is required", "red", 1, 1)
                    time.sleep(1)
                    continue

                requests.request(
                    data.get("method", "GET"),
                    data["url"],
                    params=data.get("params", {}),
                    headers=data.get("headers", {}),
                    data=data.get("body", {}),
                )

            if service == "SNS":
                initial_text = json.dumps(
                    {"topic_arn": "", "message": {}, "subject": {}}, indent=2
                )
                data = click.edit(text=initial_text)
                data = json.loads(data)
                if not data.get("topic_arn"):
                    printer.print("topic_arn is required", "red", 1, 1)
                    time.sleep(1)
                    continue

                sns = boto3.client("sns", region_name=region)
                sns.publish(
                    TopicArn=data.get("topic_arn"),
                    Message=str(data.get("message")),
                    Subject=str(data.get("subject", {})),
                )

            if service == "SQS":
                initial_text = json.dumps({"queue_url": "", "message": {}}, indent=2)
                data = click.edit(text=initial_text)
                data = json.loads(data)
                if not data.get("queue_url") :
                    printer.print("queue_url is required", "red", 1, 1)
                    time.sleep(1)
                    continue

                sqs = boto3.client("sqs", region_name=region)
                sqs.send_message(
                    QueueUrl=data["queue_url"], MessageBody=str(data["message"])
                )

            if service == "S3":
                initial_text = json.dumps(
                    {"bucket_name": "", "file_path": "", "metadata": {}}, indent=2
                )
                data = click.edit(text=initial_text)
                data = json.loads(data)
                if not data.get("bucket_name") or not data.get("file_path"):
                    printer.print("bucket_name and file_path are required", "red", 1, 1)
                    time.sleep(1)
                    continue

                filename = data["file_path"].split("/")[-1]
                s3_client = boto3.client("s3")
                with open(data["file_path"], "rb") as file:
                    s3_client.put_object(
                        Bucket=data["bucket_name"],
                        Key=filename,
                        Body=file,
                        Metadata=data.get("metadata", {}),
                    )

            if service == "Event Bridge":
                initial_text = json.dumps({"bus_name": "", "message": {}}, indent=2)
                data = click.edit(text=initial_text)
                data = json.loads(data)
                if not data.get("bus_name"):
                    printer.print("bus_name is required", "red", 1, 1)
                    time.sleep(1)
                    continue

                event = {
                    "Source": "event.bridge",
                    "DetailType": "UserAction",
                    "Detail": json.dumps({"message": data["message"]}),
                    "EventBusName": data["bus_name"],
                }
                event_client = boto3.client("events", region_name=region)
                event_client.put_events(Entries=[event])

        except Exception as e:
            printer.print(str(e), "red", 1, 1)
            time.sleep(4)
            continue
