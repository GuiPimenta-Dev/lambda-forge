import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as targets

from lambda_forge.trackers import trigger


class Bus:
    def __init__(self, scope, context) -> None:
        self.scope = scope
        self.context = context

    @trigger(service="event_bridge", trigger="rule_name", function="function")
    def schedule(self, rule_name, expression, function):
        events.Rule(
            self.scope,
            rule_name,
            schedule=events.Schedule.expression(expression),
            targets=[targets.LambdaFunction(handler=function)],
        )
