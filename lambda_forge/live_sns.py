import json

import boto3
import click


class LiveSNS:
    def __init__(self, region, printer):
        self.sns = boto3.client("sns", region_name=region)
        self.printer = printer
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.topic_arn = self.sns.create_topic(Name="Live-Topic")["TopicArn"]

    def subscribe(self, function_arn, stub_name):
        self.printer.change_spinner_legend("Subscribing to SNS Topic")
        self.lambda_client.add_permission(
            FunctionName=stub_name,
            StatementId="sns_invoke",
            Action="lambda:InvokeFunction",
            Principal="sns.amazonaws.com",
            SourceArn=self.topic_arn,
        )

        self.sns.subscribe(TopicArn=self.topic_arn, Protocol="lambda", Endpoint=function_arn)

        return self.topic_arn

    def publish(self, subject, msg_attributes):
        self.printer.show_banner("SNS")
        self.printer.log(f"Subject: {subject}", "white", 1)
        self.printer.log(f"Message Attributes: {msg_attributes}", "white", 1, 1)

        if msg_attributes:
            try:
                message_attributes = json.loads(msg_attributes)
                if not isinstance(message_attributes, dict):
                    self.log_failure(self.printer)
                    exit()

            except:
                self.log_failure(self.printer)
                exit()

        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        try:
            self.sns.publish(TopicArn=self.topic_arn, Message=message, Subject=subject, MessageAttributes=message_attributes)
        except:
            self.log_failure(self.printer)

    @staticmethod
    def log_failure(printer):
        printer.log("Failed to Publish Message!", "red")
        printer.log("Example of a Valid Payload: ", "gray", 1)
        payload = {
            "message": "Hello World!",
            "subject": "Hello World!",
            "message_attributes": {"Author": {"StringValue": "Daniel", "DataType": "String"}},
        }
        printer.log(json.dumps(payload, indent=4), "gray", 1, 1)

    @staticmethod
    def parse_logs(event):
        event = event["Records"][0]["Sns"]
        message = event["Message"]
        subject = event.get("Subject", "")
        message_attributes = event.get("MessageAttributes", {})

        return {
            "Records": [
                {
                    "Sns": {
                        "Message": message,
                        "Subject": subject,
                        "MessageAttributes": message_attributes,
                    }
                }
            ]
        }
