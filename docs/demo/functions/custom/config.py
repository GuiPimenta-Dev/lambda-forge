from infra.services import Services


class CustomConfig:
    def __init__(self, services: Services) -> None:

        function = services.aws_lambda.create_function(
            name="Custom",
            path="./functions/custom",
            description="A function to make use of the custom layer",
            layers=[services.layers.my_custom_layer],
        )

        services.api_gateway.create_endpoint("GET", "/custom", function, public=True)
