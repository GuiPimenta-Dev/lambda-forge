import ast
import time
import uuid

import boto3
import click


class LiveS3:
    def __init__(self, region, printer):
        self.printer = printer
        self.s3_client = boto3.client("s3")
        self.lambda_client = boto3.client("lambda")
        self.region = region

    def subscribe(self, function_arn, account_id):

        try:
            self.printer.change_spinner_legend("Setting up Lambda Trigger for S3 Bucket")
            bucket_name = f"live-s3-{uuid.uuid4()}"

            existing_buckets = self.s3_client.list_buckets()["Buckets"]
            for bucket in existing_buckets:
                if bucket["Name"].startswith("live-s3-"):
                    object_list = self.s3_client.list_objects(Bucket=bucket["Name"])
                    if "Contents" in object_list:
                        for obj in object_list["Contents"]:
                            self.s3_client.delete_object(Bucket=bucket["Name"], Key=obj["Key"])
                    self.s3_client.delete_bucket(Bucket=bucket["Name"])

            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.region},
            )

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

            time.sleep(6)
            self.lambda_client.add_permission(FunctionName=function_arn, StatementId=f"{bucket_name}-invoke", Action="lambda:InvokeFunction", Principal="s3.amazonaws.com", SourceArn=f"arn:aws:s3:::{bucket_name}", SourceAccount=account_id)

            # Set the notification configuration on the bucket
            self.s3_client.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration={"LambdaFunctionConfigurations": [lambda_config]},
            )

            return f"arn:aws:s3:::{bucket_name}"

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
