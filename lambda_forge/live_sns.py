import json
import sys
import boto3
import click
import pyfiglet
import os

class LiveSNS:
    def __init__(self, region, logger):
        self.sns = boto3.client("sns", region_name=region)
        self.logger = logger
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.topic_arn = self.sns.create_topic(Name="Live-Server-Topic")["TopicArn"]

    def subscribe(self, function_arn, stub_name):
        self.logger.change_spinner_legend("Subscribing to SNS Topic")
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
        print("\033[H\033[J", end="")
        os.system("clear")
        text = f"Trigger SNS"
        ascii_art = pyfiglet.figlet_format(text, width=200)
        self.logger.log(ascii_art, "rose", 1)
        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        self.sns.publish(TopicArn=self.topic_arn, Message=message)
