from infra.services import Services


class HelloConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Hello",
            path="./functions/hello",
            description="A private function",
        )

        services.api_gateway.create_endpoint("GET", "/hello", function, authorizer="jwt")