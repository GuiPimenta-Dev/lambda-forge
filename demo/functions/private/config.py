from infra.services import Services


class PrivateConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Private",
            path="./functions/private",
            description="A private function",
        )

        services.api_gateway.create_endpoint("GET", "/private", function)
