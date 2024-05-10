import json
import uuid

import boto3
import click


class LiveEvent:
    def __init__(self, region, printer):
        self.event_client = boto3.client("events", region_name=region)
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.printer = printer
        self.region = region
        self.bus_name = "Live-Event"
        self.ensure_bus_exists()

    def ensure_bus_exists(self):
        buses = self.event_client.list_event_buses(NamePrefix=self.bus_name)
        bus_exists = any(bus["Name"] == self.bus_name for bus in buses["EventBuses"])

        if bus_exists:
            rules = self.event_client.list_rules(EventBusName=self.bus_name)
            for rule in rules["Rules"]:
                targets = self.event_client.list_targets_by_rule(Rule=rule["Name"], EventBusName=self.bus_name)
                target_ids = [target["Id"] for target in targets["Targets"]]
                if target_ids:
                    self.event_client.remove_targets(Rule=rule["Name"], EventBusName=self.bus_name, Ids=target_ids)
                self.event_client.delete_rule(Name=rule["Name"], EventBusName=self.bus_name)
            self.event_client.delete_event_bus(Name=self.bus_name)

        self.event_client.create_event_bus(Name=self.bus_name)

    def subscribe(self, function_arn, account_id):
        # self.printer.change_spinner_legend("Creating EventBridge rule")

        rule_name = f"Live-Rule"
        # Add permission for EventBridge to invoke Lambda
        self.lambda_client.add_permission(FunctionName=function_arn, StatementId=str(uuid.uuid4()), Action="lambda:InvokeFunction", Principal="events.amazonaws.com", SourceArn=f"arn:aws:events:{self.region}:{account_id}:rule/{self.bus_name}/{rule_name}")

        # Create or update rule to target Lambda
        self.event_client.put_rule(Name=rule_name, EventBusName=self.bus_name, EventPattern=json.dumps({"source": ["my.application"]}), State="ENABLED")
        self.event_client.put_targets(Rule=rule_name, EventBusName=self.bus_name, Targets=[{"Id": "target1", "Arn": function_arn}])

        return f"arn:aws:events:{self.region}:{account_id}:event-bus/{self.bus_name}"

    def publish(self):
        # self.printer.show_banner("Event Bridge")
        event = {"Source": "my.application", "DetailType": "UserAction", "Detail": json.dumps({"message": click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)}), "EventBusName": self.bus_name}
        self.event_client.put_events(Entries=[event])


# Example usage
lambda_arn = "arn:aws:lambda:us-east-2:211125768252:function:HelloJhony-Live"
e = LiveEvent("us-east-2", "qew")
e.subscribe(lambda_arn, "211125768252")
e.publish()
