from aws_cdk.aws_sns import Topic


class SNS:
    def __init__(self, scope, arns) -> None:
        self.alarm_topic = Topic.from_topic_arn(
            scope,
            id="AlarmTopic",
            topic_arn=arns["alarm_topic_arn"],
        )