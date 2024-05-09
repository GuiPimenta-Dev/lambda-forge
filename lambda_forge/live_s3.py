import json
import boto3
import click

from lambda_forge.live_iam import LiveIAM

class LiveS3:
    def __init__(self, region, printer):
        self.iam = LiveIAM(region)
        self.printer = printer
        self.s3_client = boto3.client("s3", region_name=region)

    def subscribe(self, function_arn, stub_name):
        self.printer.change_spinner_legend("Setting up Lambda Trigger for S3 Bucket")

        response = self.s3_client.put_bucket_notification_configuration(
        Bucket="Live-S3",
        NotificationConfiguration= {'LambdaFunctionConfigurations':[{'LambdaFunctionArn': function_arn, 'Events': ['s3:*:*']}]})
        
        bucket_name = f"{lib}-layer-" + str(uuid.uuid4())

    existing_buckets = s3_client.list_buckets()["Buckets"]
    bucket = None
    for existing_bucket in existing_buckets:
        name = existing_bucket["Name"]
        if f"{lib}-layer-" in name:
            bucket = existing_bucket
            break

    if not bucket:
        bucket = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": region})

    s3_client.upload_file(lib_zip, bucket["Name"], lib_zip)
                        
        return response["bucket"]

    def publish(self):
        self.printer.show_banner("SQS")

        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message,
        )

    @staticmethod
    def parse_logs(event):
        record = event["Records"][0]
        message_body = record["body"]
        message_attributes = record.get("messageAttributes", {})

        return {
            "Records": [
                {
                    "body": message_body,
                    "messageAttributes": message_attributes,
                }
            ]
        }
