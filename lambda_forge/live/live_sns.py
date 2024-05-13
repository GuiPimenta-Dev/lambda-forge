import boto3
import click
import uuid


class LiveSNS:
    def __init__(self, region, account, printer):
        self.sns = boto3.client("sns", region_name=region)
        self.printer = printer
        self.region = region
        self.account = account
        self.lambda_client = boto3.client("lambda", region_name=region)

    def create_or_get_topic(self, topic_name):
        existent_topics = self.sns.list_topics()
        topics = existent_topics["Topics"]
        for topic in topics:
            if topic["TopicArn"] == f"arn:aws:sns:{self.region}:{self.account}:{topic_name}":
                return topic["TopicArn"]

        return self.sns.create_topic(Name=topic_name)["TopicArn"]

    def create_trigger(self, function_arn, stub_name, topic_arn):
        self.lambda_client.add_permission(
            FunctionName=stub_name,
            StatementId=str(uuid.uuid4()),
            Action="lambda:InvokeFunction",
            Principal="sns.amazonaws.com",
            SourceArn=topic_arn,
        )

        self.sns.subscribe(TopicArn=topic_arn, Protocol="lambda", Endpoint=function_arn)

        trigger = {
            "Trigger": "SNS",
            "Arn": topic_arn,
        }
        return trigger

    def publish(self):
        self.printer.show_banner("SNS")
        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        self.sns.publish(TopicArn=self.topic_arn, Message=message)
