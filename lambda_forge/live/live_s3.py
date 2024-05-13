import ast
import uuid

import boto3
import click


class LiveS3:
    def __init__(self, region, printer):
        self.printer = printer
        self.s3_client = boto3.client("s3")
        self.lambda_client = boto3.client("lambda")
        self.region = region

    def create_bucket(self, bucket_name):
        self.s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": self.region},
        )

    def subscribe(self, function_arn, account_id, bucket_name):

        try:
            events = [
                "s3:ObjectCreated:*",
                "s3:ObjectRemoved:*",
                "s3:ObjectRestore:*",
                "s3:ReducedRedundancyLostObject",
            ]

            lambda_config = {
                "LambdaFunctionArn": function_arn,
                "Events": events,
            }
            self.lambda_client.add_permission(
                FunctionName=function_arn,
                StatementId=str(uuid.uuid4()),
                Action="lambda:InvokeFunction",
                Principal="s3.amazonaws.com",
                SourceArn=f"arn:aws:s3:::{bucket_name}",
                SourceAccount=account_id,
            )

            # Set the notification configuration on the bucket
            self.s3_client.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration={"LambdaFunctionConfigurations": [lambda_config]},
            )

            trigger = {"Trigger": "S3", "ARN": f"arn:aws:s3:::{bucket_name}"}
            return trigger

        except Exception as e:
            print(f"Error in subscribe method: {e}")
            raise e

    def publish(self):
        self.printer.show_banner("S3")
        metadata = click.prompt(click.style("Metadata", fg=(37, 171, 190)), type=str, default="{}", show_default=False)
        file_path = click.prompt(click.style("File Path", fg=(37, 171, 190)), type=str)
        filename = file_path.split("/")[-1]

        bucket_name = None
        existing_buckets = self.s3_client.list_buckets()["Buckets"]
        for bucket in existing_buckets:
            if bucket["Name"].startswith("live-s3-"):
                bucket_name = bucket["Name"]
                break

        metadata = ast.literal_eval(metadata)

        with open(file_path, "rb") as file:
            self.s3_client.put_object(Bucket=bucket_name, Key=filename, Body=file, Metadata=metadata)
