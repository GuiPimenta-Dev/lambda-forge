from infra.services import Services


class GetMeConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="GetMe", path="./functions/blog", description="Get the current user", directory="get_me"
        )

        services.api_gateway.create_endpoint("GET", "/blog/me", function, authorizer="cognito")
