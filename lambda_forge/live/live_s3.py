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
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
        except:
            self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': self.region}
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
