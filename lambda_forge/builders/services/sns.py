from aws_cdk import aws_lambda_event_sources
from aws_cdk import aws_sns as sns

from lambda_forge.trackers import invoke, trigger


class SNS:
    def __init__(self, scope, resources) -> None:

        # self.sns_topic = sns.Topic.from_topic_arn(
        #     scope,
        #     id="SNSTopic",
        #     topic_arn=resources["arns"]["sns_topic_arn"],
        # )
        ...

    @trigger(service="sns", trigger="topic", function="function")
    def create_trigger(self, topic, function):
        topic = getattr(self, topic)
        sns_subscription = aws_lambda_event_sources.SnsEventSource(topic)
        function.add_event_source(sns_subscription)

    @invoke(service="sns", resource="topic", function="function")
    def grant_publish(self, topic, function):
        topic = getattr(self, topic)
        topic.grant_publish(function)
