import json
import uuid
import boto3
import click

from lambda_forge.live_iam import LiveIAM


class LiveS3:
    def __init__(self, region, printer):
        self.iam = LiveIAM(region)
        self.printer = printer
        self.s3_client = boto3.client("s3", region_name=region)
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.region = region

    def subscribe(self, function_arn, stub_name):
        # self.printer.change_spinner_legend("Setting up Lambda Trigger for S3 Bucket")

        existing_buckets = self.s3_client.list_buckets()["Buckets"]
        self.bucket_name = None
        for existing_bucket in existing_buckets:
            name = existing_bucket["Name"]
            if "live-s3-" in name:
                self.bucket_name = existing_bucket["Name"]
                break

        if not self.bucket_name:
            self.bucket_name = f"live-s3-" + str(uuid.uuid4())
            self.s3_client.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration={"LocationConstraint": self.region})

        s3_arn = f"arn:aws:s3:::{self.bucket_name}"

        response = self.lambda_client.add_permission(
            FunctionName=stub_name,
            StatementId=str(uuid.uuid4()),
            Action="lambda:InvokeFunction",
            Principal="s3.amazonaws.com",
            SourceArn=s3_arn,
        )

        self.s3_client.put_bucket_notification_configuration(
            Bucket=self.bucket_name,
            NotificationConfiguration={
                "LambdaFunctionConfigurations": [
                    {
                        "LambdaFunctionArn": function_arn,
                        "Events": [
                            "s3:ObjectCreated:*",
                            "s3:ObjectRemoved:*",
                            "s3:ObjectRestore:*",
                        ],
                    }
                ]
            },
        )

        return s3_arn

    def publish(self):
        self.printer.show_banner("S3")
        metadata = click.prompt(click.style("Metadata", fg=(37, 171, 190)), type=str)
        file_path = click.prompt(click.style("File Path", fg=(37, 171, 190)), type=str)
        filename = file_path.split("/")[-1]

        with open(file_path, "rb") as file:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=filename, Body=file, Metadata=metadata)

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


s3 = LiveS3("us-east-2", "printer").subscribe("arn:aws:lambda:us-east-2:211125768252:function:Vixi-Live", "Vixi-Live")
