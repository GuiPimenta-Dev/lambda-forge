from aws_cdk import aws_sns as sns

from lambda_forge.services import Publisher


class SNS(Publisher):
    def __init__(self, scope, resources) -> None:

        # self.sns_topic = sns.Topic.from_topic_arn(
        #     scope,
        #     id="SNSTopic",
        #     topic_arn=resources["arns"]["sns_topic_arn"],
        # )
        ...
