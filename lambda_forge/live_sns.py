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

    def publish(self):
        self.printer.show_banner("SNS")
        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        self.sns.publish(TopicArn=self.topic_arn, Message=message)

    @staticmethod
    def parse_logs(event):
        event = event["Records"][0]["Sns"]
        message = event["Message"]

        return {
            "Records": [
                {
                    "Sns": {
                        "Message": message,
                    }
                }
            ]
        }
