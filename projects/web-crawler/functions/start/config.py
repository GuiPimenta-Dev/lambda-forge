from infra.services import Services


class StartConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Start",
            path="./functions/start",
            description="handle start command",
            environment={"CRAWLER_QUEUE_NAME": services.sqs.crawler_queue.queue_name},
        )

        services.api_gateway.create_endpoint("POST", "/start", function, public=True)

        services.sqs.grant_send_messages("crawler_queue", function)
