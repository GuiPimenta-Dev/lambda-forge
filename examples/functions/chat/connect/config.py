from infra.services import Services


class ConnectConfig:
    def __init__(self, services: Services) -> None:

        send_connection_id_function = services.aws_lambda.functions["SendConnectionId"]

        connect_function = services.aws_lambda.create_function(
            name="Connect",
            path="./functions/chat",
            description="Handle the websocket connection",
            directory="connect",
            environment={
                "TARGET_FUNCTION_ARN": send_connection_id_function.function_arn,
            },
        )

        services.websockets.create_route("$connect", connect_function)

        send_connection_id_function.grant_invoke(connect_function)