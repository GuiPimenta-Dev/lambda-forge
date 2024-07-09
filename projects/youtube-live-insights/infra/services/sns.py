from aws_cdk import aws_lambda_event_sources
from aws_cdk import aws_sns as sns
from aws_cdk.aws_sns import Topic
from lambda_forge.trackers import invoke, trigger


class SNS:
    def __init__(self, scope, context) -> None:

        self.videos_topic = Topic.from_topic_arn(
            scope,
            "VideosTopic",
            topic_arn=context.resources["arns"]["videos_topic_arn"],
        )

    @trigger(service="sns", trigger="topic", function="function")
    def create_trigger(self, topic, function):
        topic = getattr(self, topic)
        sns_subscription = aws_lambda_event_sources.SnsEventSource(topic)
        function.add_event_source(sns_subscription)

    @invoke(service="sns", resource="topic", function="function")
    def grant_publish(self, topic, function):
        topic = getattr(self, topic)
        topic.grant_publish(function)
