from aws_cdk import aws_sqs as sqs

from lambda_forge.services import Queue


class SQS(Queue):
    def __init__(self, scope, resources) -> None:

        # self.sqs = sqs.Queue.from_queue_arn(
        #     scope,
        #     "SQS",
        #     queue_arn=resources["arns"]["sqs_arn"],
        # )
        ...
