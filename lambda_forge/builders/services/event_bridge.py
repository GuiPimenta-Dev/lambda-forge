from aws_cdk import aws_sns as sns

from lambda_forge.services import Bus


class EventBridge(Bus):
    def __init__(self, scope, context) -> None:
        super().__init__(scope=scope, context=context)

        # self.event_bridge = events.EventBus.from_event_bus_arn(
        #     scope,
        #     id="EventBridge",
        #     event_bus_arn=context.resources["arns"]["event_bridge_arn"],
        # )
        ...
