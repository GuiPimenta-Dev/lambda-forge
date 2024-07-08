from infra.services import Services


class ExternalConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="External",
            path="./functions/external",
            description="A function that uses an external library",
            layers=[services.layers.requests_layer],
        )

        services.api_gateway.create_endpoint("GET", "/external", function, public=True)
