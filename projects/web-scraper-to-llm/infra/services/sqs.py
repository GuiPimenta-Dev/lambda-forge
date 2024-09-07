from aws_cdk import Duration, aws_lambda_event_sources
from aws_cdk import aws_sqs as sqs
from lambda_forge.trackers import invoke, trigger


class SQS:
    def __init__(self, scope, context) -> None:

        self.crawler_queue = sqs.Queue(
            scope,
            "CrawlerQueue",
            queue_name="CrawlerQueue",
            visibility_timeout=Duration.seconds(900),
        )

        self.crawler_queue_dlq = sqs.Queue(
            scope,
            "CrawlerQueueDLQ",
            queue_name="CrawlerQueueDLQ",
            visibility_timeout=Duration.seconds(900),
        )

    @trigger(service="sqs", trigger="queue", function="function")
    def create_trigger(self, queue, function):
        queue = getattr(self, queue)
        event_source = aws_lambda_event_sources.SqsEventSource(queue)
        function.add_event_source(event_source)
        queue.grant_consume_messages(function)

    @invoke(service="sqs", resource="queue", function="function")
    def grant_send_messages(self, queue, function):
        queue = getattr(self, queue)
        queue.grant_send_messages(function)
