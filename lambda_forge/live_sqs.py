import json
import boto3
import click

from lambda_forge.live_iam import LiveIAM
from botocore.exceptions import ClientError


class LiveSQS:
    def __init__(self, region, printer):
        self.sqs = boto3.client("sqs", region_name=region)
        self.iam = LiveIAM(region)
        self.iam_client = boto3.client("iam", region_name=region)
        self.printer = printer
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.queue_url = self.sqs.create_queue(QueueName="Live-Queue")["QueueUrl"]
        response = self.sqs.get_queue_attributes(QueueUrl=self.queue_url, AttributeNames=["QueueArn"])
        self.queue_arn = response["Attributes"]["QueueArn"]

    def subscribe(self, function_arn, stub_name):
        self.printer.change_spinner_legend("Setting up Lambda Trigger for SQS Queue")

        try:

            policy = {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": "sqs:*", "Resource": "*"}],
            }

            self.iam = self.iam.attach_policy_to_lambda(policy, function_arn)

            self.sqs.set_queue_attributes(QueueUrl=self.queue_url, Attributes={"VisibilityTimeout": "900"})

            self.delete_triggers()

            self.lambda_client.create_event_source_mapping(EventSourceArn=self.queue_arn, FunctionName=function_arn, Enabled=True)

            return self.queue_arn
        except Exception as e:
            self.printer.print(f"Error setting up Lambda trigger: {str(e)}", "red")
            return None

    def publish(self):
        self.printer.show_banner("SQS")

        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        try:
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message,
            )
        except:
            self.print_failure(self.printer)

    @staticmethod
    def print_failure(printer):
        printer.print("Failed to Publish Message!", "red")
        printer.print("Example of a Valid Payload: ", "gray", 1)
        payload = {
            "message": "Hello World!",
            "message_attributes": {"Author": {"StringValue": "Daniel", "DataType": "String"}},
        }
        printer.print(json.dumps(payload, indent=4), "gray", 1, 1)

    def delete_triggers(self):
        response = self.lambda_client.list_event_source_mappings(EventSourceArn=self.queue_arn)

        for mapping in response["EventSourceMappings"]:
            mapping_id = mapping["UUID"]
            self.lambda_client.delete_event_source_mapping(UUID=mapping_id)

    @staticmethod
    def parse_logs(event):
        record = event["Records"][0]
        message_body = record["body"]

        return {"Records": [{"body": message_body}]}
