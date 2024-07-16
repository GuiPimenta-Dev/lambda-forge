from infra.services import Services

class BotConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Bot",
            path="./functions/telegram",
            description="telegram bot",
            directory="bot"
        )

        services.api_gateway.create_endpoint("GET", "/telegram", function, public=True)

            