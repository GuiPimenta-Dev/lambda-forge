from aws_cdk.aws_sns import Topic


class SNS:
    def __init__(self, scope) -> None:

        self.alarm_topic = Topic.from_topic_arn(
            scope,
            id="AlarmTopic",
            topic_arn="",
        )
