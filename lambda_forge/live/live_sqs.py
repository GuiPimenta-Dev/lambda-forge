import uuid

import boto3
import click

from lambda_forge.live.live_iam import LiveIAM


class LiveSQS:
    def __init__(self, region, printer):
        self.sqs = boto3.client("sqs", region_name=region)
        self.iam = LiveIAM(region)
        self.iam_client = boto3.client("iam", region_name=region)
        self.printer = printer
        self.lambda_client = boto3.client("lambda", region_name=region)

    def create_queue(self, name):
        queue_url = self.sqs.create_queue(QueueName=name)["QueueUrl"]
        response = self.sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["QueueArn"])
        return queue_url, response["Attributes"]["QueueArn"]

    def subscribe(self, function_arn, queue_url, queue_arn):

        policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": "sqs:*", "Resource": "*"}],
        }

        self.iam = self.iam.attach_policy_to_lambda(policy, function_arn, str(uuid.uuid4()))

        self.sqs.set_queue_attributes(QueueUrl=queue_url, Attributes={"VisibilityTimeout": "900"})

        self.lambda_client.create_event_source_mapping(
            EventSourceArn=queue_arn, FunctionName=function_arn, Enabled=True
        )

        trigger = {
            "trigger": "SQS",
            "url": queue_url,
        }
        return trigger

    def publish(self):
        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message,
            Subject="Message from Lambda Forge",
        )
