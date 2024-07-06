from infra.services import Services


class CallbackConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Callback",
            path="./functions/blog",
            description="SSO callback",
            directory="callback"
        )

        services.api_gateway.create_endpoint("GET", "/callback", function, authorizer="cognito")

            