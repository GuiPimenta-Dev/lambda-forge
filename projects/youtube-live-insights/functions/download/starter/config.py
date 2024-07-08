from infra.services import Services


class StarterConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="StartDownload",
            path="./functions/download",
            directory="starter",
            description="Start the process",
            environment={
                "DOWNLOADS_QUEUE_URL": services.sqs.downloads_queue.queue_url,
            },
        )

        services.api_gateway.create_endpoint("POST", "/start", function, public=True)

        services.sqs.grant_send_messages("downloads_queue", function)
