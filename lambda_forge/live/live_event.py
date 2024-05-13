import json
import uuid

import boto3
import click


class LiveEventBridge:
    def __init__(self, region, printer):
        self.event_client = boto3.client("events", region_name=region)
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.printer = printer
        self.region = region

    def create_bus(self, bus_name):
        buses = self.event_client.list_event_buses(NamePrefix=bus_name)
        bus_exists = any(bus["Name"] == bus_name for bus in buses["EventBuses"])

        if not bus_exists:
            self.event_client.create_event_bus(Name=bus_name)

    def subscribe(self, function_arn, account_id, bus_name):
        rule_name = "Live-Rule"
        self.lambda_client.add_permission(
            FunctionName=function_arn,
            StatementId=str(uuid.uuid4()),
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=f"arn:aws:events:{self.region}:{account_id}:rule/{bus_name}/{rule_name}",
        )

        # Create or update rule to target Lambda
        self.event_client.put_rule(
            Name=rule_name,
            EventBusName=bus_name,
            EventPattern=json.dumps({"source": ["my.application"]}),
            State="ENABLED",
        )
        self.event_client.put_targets(
            Rule=rule_name,
            EventBusName=bus_name,
            Targets=[{"Id": "target1", "Arn": function_arn}],
        )

        trigger = {"Trigger": "Event Bridge", "ARN": f"arn:aws:events:{self.region}:{account_id}:event-bus/{bus_name}"}
        return trigger

    def publish(self):
        self.printer.show_banner("Event Bridge")
        event = {
            "Source": "my.application",
            "DetailType": "UserAction",
            "Detail": json.dumps(
                {
                    "message": click.prompt(
                        click.style("Message", fg=(37, 171, 190)), type=str, default="", show_default=False
                    )
                }
            ),
            "EventBusName": self.bus_name,
        }
        self.event_client.put_events(Entries=[event])
