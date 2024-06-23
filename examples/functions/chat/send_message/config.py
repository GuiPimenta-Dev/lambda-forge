from infra.services import Services

class SendMessageConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="SendMessage",
            path="./functions/chat",
            description="Send messages to sender and recipient",
            directory="send_message"
        )

        services.websockets.create_route("", function)

            